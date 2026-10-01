"""Helpers shared by the tests of the mess: datasets by setting, the profile's numbers, and rates
checked within three standard errors of the profile's number at the size actually measured."""

import csv
import math
from functools import cache
from pathlib import Path

import pytest

from emva_sim import dataset, profile
from emva_sim.intake import RowKind

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
TRUTH = "hidden-truth/hidden-truth.csv"
STAGES = "hidden-truth/stage-history.csv"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def raw():
    return profile.load(PROFILE)


@cache
def resolved(setting):
    """The profile with every range resolved for the setting (shared: do not change it)."""
    return profile.resolve(raw(), setting)


def number(setting, name):
    """The number a range resolves to at a setting, by its dotted name."""
    node = resolved(setting)
    for key in name.split("."):
        node = node[key]
    return node


def ends(name):
    """The middle and the range's low and high ends, one at a time."""
    return ["middle", f"{name}@low", f"{name}@high"]


def three_standard_errors(rate, n):
    return 3 * math.sqrt(rate * (1 - rate) / n)


def assert_rate(hits, n, rate):
    """hits of n is the rate, within three standard errors at n."""
    assert n
    assert hits / n == pytest.approx(rate, abs=three_standard_errors(rate, n)), (hits, n, rate)


def assert_exponential_median(values, median):
    """The sample median of exponential draws is the median, within three standard errors."""
    n = len(values)
    tolerance = 3 * median / (math.log(2) * math.sqrt(n))
    observed = sorted(values)[n // 2]
    assert observed == pytest.approx(median, abs=tolerance), (observed, n, median)


def kinds(folder, kind):
    return [r for r in rows(folder / TRUTH) if r["row_kind"] == kind]


def genuine(folder):
    """The deal Record IDs of genuine Leads, without duplicates and bots."""
    return {r["deal_record_id"] for r in kinds(folder, RowKind.LEAD)}


@pytest.fixture(scope="session")
def generate(tmp_path_factory):
    """The dataset at a setting and history, seed 1, generated once per test session."""
    made = {}

    def at(setting, history):
        if (setting, history) not in made:
            out = tmp_path_factory.mktemp("out")
            made[setting, history] = dataset.generate(
                PROFILE, setting, seed=1, out=out, history=history
            )
        return made[setting, history]

    return at
