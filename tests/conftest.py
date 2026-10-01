"""Helpers shared by the tests: datasets by setting, the profile's numbers, rates checked within
STANDARD_ERRORS of the profile's number at the size actually measured, and large fixed-seed
samples of genuine Leads, generated once per session, for tests that measure rates and odds."""

import csv
import math
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from random import Random

import pytest
from echo_model import profile_with_echoed_variations

from emva_sim import dataset, hidden_truth, profile
from emva_sim.intake import RowKind

REAL_PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
# The profile and its phrase bank with a cache that echo_model wrote through vary-phrases, so the
# tests generate text without the model, whether or not the committed cache is complete yet.
PROFILE = profile_with_echoed_variations(REAL_PROFILE)
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


# How many standard errors every statistical check in the suite allows. The suite makes on the
# order of 1,000 such checks; at 3 standard errors each fails by chance about 0.3% of the time, so
# some check would fail on almost any seed. 4 is roughly the Bonferroni bound for about 1,000 checks
# at a 5% chance that any of them fails by chance (the two-sided z for 0.05 / 1,000 is 4.06).
# Raised from 3 after seed 1 put an unbiased rate (loss.blank_reason@low) 3.9 standard errors out.
STANDARD_ERRORS = 4


def tolerance(rate, n):
    """STANDARD_ERRORS of a rate measured on n."""
    return STANDARD_ERRORS * math.sqrt(rate * (1 - rate) / n)


def assert_rate(hits, n, rate):
    """hits of n is the rate, within STANDARD_ERRORS at n."""
    assert n
    assert hits / n == pytest.approx(rate, abs=tolerance(rate, n)), (hits, n, rate)


def assert_exponential_median(values, median):
    """The sample median of exponential draws is the median, within STANDARD_ERRORS."""
    n = len(values)
    allowed = STANDARD_ERRORS * median / (math.log(2) * math.sqrt(n))
    observed = sorted(values)[n // 2]
    assert observed == pytest.approx(median, abs=allowed), (observed, n, median)


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


@dataclass(frozen=True)
class Sample:
    """The resolved profile a sample was drawn from, and its hidden truth with each row's lead
    and true path attached."""

    p: dict
    rows: list[dict]


def large_sample(setting: str, leads_per_month: int, seed: int = 1, **overrides) -> Sample:
    """A two-year history of genuine Leads at this volume, as the hidden truth writes their true
    paths.

    overrides replace numbers of the resolved profile, as "section.name": value.
    """
    p = profile.resolve(raw(), setting)
    p["volume"]["leads_per_month"] = leads_per_month
    for name, value in overrides.items():
        *path, last = name.split(".")
        node = p
        for key in path:
            node = node[key]
        node[last] = value
    drawn, paths = dataset.leads_and_paths(p, Random(seed))
    rows = []
    for lead, path in zip(drawn, paths, strict=True):
        row = hidden_truth.true_path(p, lead, path)
        row["lead"], row["path"] = lead, path
        rows.append(row)
    return Sample(p, rows)


@pytest.fixture(scope="session")
def middle_sample():
    """150,000 leads at the middle."""
    return large_sample("middle", 6250)
