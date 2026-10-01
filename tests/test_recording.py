"""How the sales team records each Lead's true path, on simulated data.

One fixed seed, six months of leads, exported long after the last one so nearly every stage change
is recorded before the export. Each rate's tolerance is about three standard errors at that size,
written before the numbers were looked at.
"""

import csv
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, time
from pathlib import Path

import pytest

from emva_sim import dataset

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2025, 12, 31))
DEALS = "export/deals-and-contacts-only/hubspot-crm-exports-safari-enquiries-2025-12-31.csv"
TRUTH = "hidden-truth/hidden-truth.csv"
STAGES = "hidden-truth/stage-history.csv"
EXPORT = "2025-12-31 00:00"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def entered(stage):
    return f'Date entered "{stage} (Safari Enquiries)"'


@pytest.fixture(scope="module")
def middle(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    return dataset.generate(PROFILE, "middle", seed=1, out=out, history=HISTORY)


def history_by_deal(folder):
    by_deal = defaultdict(list)
    for change in rows(folder / STAGES):
        by_deal[change["deal_record_id"]].append(change)
    return by_deal


def test_the_export_shows_the_latest_recorded_entry_of_each_stage_before_the_export(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    by_deal = history_by_deal(middle)
    assert set(by_deal) == set(deals)
    for deal_id, changes in by_deal.items():
        latest = {}
        for change in changes:
            if change["recorded_entered_at"] and change["recorded_entered_at"] < EXPORT:
                latest[change["crm_stage"]] = max(
                    latest.get(change["crm_stage"], ""), change["recorded_entered_at"]
                )
        shown = {
            column: at
            for column, at in deals[deal_id].items()
            if column.startswith("Date entered") and at
        }
        assert shown == {entered(stage): at for stage, at in latest.items()}, deal_id


@pytest.fixture(scope="module")
def generated(tmp_path_factory, middle):
    made = {"middle": middle}

    def at(setting):
        if setting not in made:
            out = tmp_path_factory.mktemp("out")
            made[setting] = dataset.generate(PROFILE, setting, seed=1, out=out, history=HISTORY)
        return made[setting]

    return at


def moment(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


def days(start, end):
    return (moment(end) - moment(start)).total_seconds() / 86400


def first_lags(folder):
    """Days from each deal's first true change after New Enquiry to when it was recorded.

    Changes made in bulk are left out: they wait for the weekly review instead.
    """
    bulk = {c["recorded_entered_at"] for c in in_bulk(hand_entered(folder))}
    lags = []
    for changes in history_by_deal(folder).values():
        true = [c for c in changes if c["true_entered_at"] and c["crm_stage"] != "New Enquiry"]
        first = min(true, key=lambda c: c["true_entered_at"], default=None)
        if first and first["recorded_entered_at"] and first["recorded_entered_at"] not in bulk:
            lags.append(days(first["true_entered_at"], first["recorded_entered_at"]))
    return lags


@pytest.mark.parametrize(
    ("setting", "median", "tolerance"),
    [
        ("middle", 2, 0.2),
        ("recording.lag_days_median@low", 0, 0),
        ("recording.lag_days_median@high", 14, 1.3),
    ],
)
def test_stage_changes_are_recorded_late_by_the_profiles_median_lag(
    generated, setting, median, tolerance
):
    lags = first_lags(generated(setting))
    assert statistics.median(lags) == pytest.approx(median, abs=tolerance)


def hand_entered(folder):
    """Every recorded change but the deals' creation at New Enquiry."""
    changes = rows(folder / STAGES)
    return [c for c in changes if c["recorded_entered_at"] and c["crm_stage"] != "New Enquiry"]


def in_bulk(changes):
    """The changes whose timestamp at least two other changes share."""
    stamps = Counter(c["recorded_entered_at"] for c in changes)
    return [c for c in changes if stamps[c["recorded_entered_at"]] >= 3]


@pytest.mark.parametrize(
    ("setting", "share"),
    [
        ("middle", 0.20),
        ("recording.bulk_update_share@low", 0.05),
        ("recording.bulk_update_share@high", 0.40),
    ],
)
def test_the_profiles_share_of_stage_changes_are_made_in_bulk(generated, setting, share):
    changes = hand_entered(generated(setting))
    assert len(in_bulk(changes)) / len(changes) == pytest.approx(share, abs=0.03)


def test_bulk_updates_happen_in_the_weekly_pipeline_review(middle):
    bulk = in_bulk(hand_entered(middle))
    assert bulk
    # A deal moved through two stages at one review gets the second a minute after the first.
    for change in bulk:
        at = moment(change["recorded_entered_at"])
        assert at.strftime("%A") == "Friday" and time(16) <= at.time() <= time(18, 5), at


@pytest.mark.parametrize(
    ("setting", "share"),
    [
        ("middle", 0.30),
        ("recording.dead_left_open@low", 0.10),
        ("recording.dead_left_open@high", 0.60),
    ],
)
def test_the_profiles_share_of_lost_leads_are_left_open_at_their_last_stage(
    generated, setting, share
):
    folder = generated(setting)
    lost = [c for c in rows(folder / STAGES) if c["crm_stage"] == "Lost" and c["true_entered_at"]]
    left_open = [c for c in lost if not c["recorded_entered_at"]]
    assert len(left_open) / len(lost) == pytest.approx(share, abs=0.03)
    deals = {d["Record ID"]: d for d in rows(folder / DEALS)}
    for change in left_open:
        deal = deals[change["deal_record_id"]]
        assert deal["Deal Stage"] != "Lost" and not deal["Closed Lost Reason"]


def test_close_date_follows_the_recorded_close_not_the_true_one(middle):
    by_deal = history_by_deal(middle)
    closed = [d for d in rows(middle / DEALS) if d["Deal Stage"] in {"Deposit Paid", "Lost"}]
    assert closed
    late = 0
    for deal in closed:
        stage = deal["Deal Stage"]
        assert deal["Close Date"] == deal[entered(stage)], deal["Record ID"]
        change = next(c for c in by_deal[deal["Record ID"]] if c["crm_stage"] == stage)
        late += change["recorded_entered_at"] > change["true_entered_at"]
    assert late / len(closed) > 0.9
