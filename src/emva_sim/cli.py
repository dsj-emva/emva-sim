"""emva-sim generate: write one dataset from a profile, a setting and a seed."""

import argparse
import csv
from pathlib import Path

from emva_sim import dataset, profile


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
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        folder = dataset.generate(args.profile, args.setting, args.seed, args.out)
    except profile.UnknownSetting as error:
        parser.error(f"unknown setting {error}")
    with (folder / "hidden-truth" / "hidden-truth.csv").open(newline="", encoding="utf-8") as f:
        truth = list(csv.DictReader(f))
    won = sum(row["outcome"] == "won" for row in truth)
    print(f"Wrote {len(truth)} leads, {won} of them won, on simulated data, to {folder}")
