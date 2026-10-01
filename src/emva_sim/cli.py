"""emva-sim generate: write one dataset from a profile, a setting and a seed.
emva-sim datasets: write every dataset of the profile's sweep, from fixed seeds."""

import argparse
import csv
from pathlib import Path

from emva_sim import dataset, datasets, profile


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
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "datasets":
        listed = datasets.write_all(args.profile, args.out)
        print(f"Wrote {len(listed)} datasets, on simulated data, to {args.out}")
        return
    try:
        folder = dataset.generate(args.profile, args.setting, args.seed, args.out)
    except profile.UnknownSetting as error:
        parser.error(f"unknown setting {error}")
    with (folder / "hidden-truth" / "hidden-truth.csv").open(newline="", encoding="utf-8") as f:
        truth = list(csv.DictReader(f))
    leads = [row for row in truth if row["row_kind"] == "lead"]
    won = sum(row["outcome"] == "won" for row in leads)
    others = len(truth) - len(leads)
    print(
        f"Wrote {len(leads)} leads, {won} of them won, and {others} duplicate or bot rows,"
        f" on simulated data, to {folder}"
    )
