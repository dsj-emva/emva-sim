"""The middle dataset reproduces the profile's middle numbers, on simulated data.

One fixed seed, six months of leads (2,400 at the middle volume). Each tolerance is about three
standard errors at that size, written before the numbers were looked at.
"""

import csv
import statistics
from datetime import date, datetime
from pathlib import Path

import pytest

from emva_sim import dataset

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2024, 7, 5))
DEALS = "export/deals-and-contacts-only/hubspot-crm-exports-safari-enquiries-2024-07-05.csv"
LADDER = ["Contact attempted", "Engaged", "Qualified", "Proposal", "Won"]


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def moment(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


@pytest.fixture(scope="module")
def leads(tmp_path_factory):
    folder = dataset.generate(
        PROFILE, "middle", seed=1, out=tmp_path_factory.mktemp("o"), history=HISTORY
    )
    created = {d["Record ID"]: moment(d["Create Date"]) for d in rows(folder / DEALS)}
    truth = rows(folder / "hidden-truth" / "hidden-truth.csv")
    for row in truth:
        row["created"] = created[row["deal_record_id"]]
    return truth


def reached(leads, stage):
    return sum(
        LADDER.index(r["reached_stage"]) >= LADDER.index(stage)
        for r in leads
        if r["neglected_lead"] == "no"
    )


def test_about_one_lead_in_a_hundred_is_neglected(leads):
    share = sum(r["neglected_lead"] == "yes" for r in leads) / len(leads)
    assert share == pytest.approx(0.01, abs=0.006)


@pytest.mark.parametrize(
    ("stage", "previous", "rate", "tolerance"),
    [
        ("Engaged", "Contact attempted", 0.45, 0.03),
        ("Qualified", "Engaged", 0.95, 0.02),
        ("Proposal", "Qualified", 0.97, 0.02),
        ("Won", "Proposal", 0.25, 0.04),
    ],
)
def test_each_transition_holds_at_the_profiles_middle(leads, stage, previous, rate, tolerance):
    assert reached(leads, stage) / reached(leads, previous) == pytest.approx(rate, abs=tolerance)


def test_with_no_planted_effects_every_lead_has_the_base_propensity(leads):
    base = 0.45 * 0.95 * 0.97 * 0.25
    assert {r["win_propensity"] for r in leads} == {f"{base:.6f}"}


def test_about_ten_in_a_hundred_leads_win(leads):
    won = sum(r["outcome"] == "won" for r in leads) / len(leads)
    assert won == pytest.approx(0.10, abs=0.02)


def test_won_leads_take_about_21_days_from_submission(leads):
    days = [
        (moment(r["won_at"]) - r["created"]).total_seconds() / 86400 for r in leads if r["won_at"]
    ]
    assert statistics.median(days) == pytest.approx(21, abs=5)


def test_first_contact_attempts_follow_the_profiles_delay(leads):
    hours = [
        (moment(r["first_contact_attempt_at"]) - r["created"]).total_seconds() / 3600
        for r in leads
        if r["neglected_lead"] == "no"
    ]
    assert statistics.median(hours) == pytest.approx(4, abs=1.5)
    assert sum(h > 24 for h in hours) / len(hours) == pytest.approx(0.30, abs=0.03)


def test_deal_values_have_a_median_near_15000_and_span_5k_to_100k(leads):
    values = sorted(float(r["deal_value"]) for r in leads)
    n = len(values)
    assert 10_000 <= statistics.median(values) <= 20_000
    assert 2_500 <= values[n // 20] <= 10_000
    assert 50_000 <= values[19 * n // 20] <= 200_000


def test_half_the_leads_come_from_each_market(leads):
    share = sum(r["market_group"] == "A" for r in leads) / len(leads)
    assert share == pytest.approx(0.5, abs=0.03)


@pytest.mark.parametrize(("group", "january_share"), [("B", 1.6 / 6.6), ("A", 1.4 / 7.2)])
def test_january_carries_its_markets_seasonal_weight(leads, group, january_share):
    market = [r for r in leads if r["market_group"] == group]
    share = sum(r["created"].month == 1 for r in market) / len(market)
    assert share == pytest.approx(january_share, abs=0.03)
