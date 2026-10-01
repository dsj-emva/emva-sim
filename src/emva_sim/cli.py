"""emva-sim generate: write one dataset from a profile, a setting and a seed.
emva-sim datasets: write every dataset of the profile's sweep, from fixed seeds.
emva-sim vary-phrases: have Claude Haiku 4.5 write the cached variations of the profile's phrases.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from emva_sim import dataset, datasets, profile, vary
from emva_sim.phrases import MissingVariations


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="emva-sim")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="write the exports and the hidden truth")
    generate.add_argument("--profile", type=Path, required=True)
    generate.add_argument(
        "--setting",
        default="middle",
        help='"middle", "all-low", "all-high" or "<range name>@low" / "<range name>@high"',
    )
    generate.add_argument("--seed", type=int, default=1)
    generate.add_argument("--out", type=Path, default=Path("out"))
    sweep = commands.add_parser(
        "datasets", help="write every dataset of the profile's sweep, each with its manifest"
    )
    sweep.add_argument("--profile", type=Path, required=True)
    sweep.add_argument("--out", type=Path, default=Path("out/datasets"))
    phrases = commands.add_parser(
        "vary-phrases", help="send each uncached phrase of the bank to the model once"
    )
    phrases.add_argument("--profile", type=Path, required=True)
    phrases.add_argument(
        "--env-file", type=Path, default=Path(".env"), help=f"where to find {vary.KEY_NAME}"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "datasets":
        try:
            listed = datasets.write_all(args.profile, args.out)
        except (datasets.NotAnEarlierOutput, MissingVariations) as error:
            parser.error(str(error))
        print(f"Wrote {len(listed)} datasets, on simulated data, to {args.out}")
    elif args.command == "vary-phrases":
        _vary_phrases(parser, args)
    else:
        _generate(parser, args)


def _vary_phrases(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    try:
        key = vary.api_key(os.environ, args.env_file)
    except vary.NoApiKey as error:
        parser.error(str(error))
    model = profile.load(args.profile)["text"]["model"]
    result = vary.run(args.profile, vary.HaikuClient(key, model))
    print(
        f"{result.sent} phrases sent to {model} and cached,"
        f" {result.already_cached} already cached, {len(result.failed)} not cached"
    )
    if result.failed:
        sys.exit(1)


def _generate(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    try:
        folder = dataset.generate(args.profile, args.setting, args.seed, args.out)
    except profile.UnknownSetting as error:
        parser.error(f"unknown setting {error}")
    except MissingVariations as error:
        parser.error(str(error))
    with (folder / "hidden-truth" / "hidden-truth.csv").open(newline="", encoding="utf-8") as f:
        truth = list(csv.DictReader(f))
    leads = [row for row in truth if row["row_kind"] == "lead"]
    won = sum(row["outcome"] == "won" for row in leads)
    others = len(truth) - len(leads)
    print(
        f"Wrote {len(leads)} leads, {won} of them won, and {others} duplicate or bot rows,"
        f" on simulated data, to {folder}"
    )
