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

from emva_sim import dataset, profile

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


OPEN_AFTER_CREATION = {
    "Attempting Contact",
    "In Discussion",
    "Planning",
    "Itinerary Sent",
    "Provisional Hold",
}
CLOSED = {"Deposit Paid", "Lost"}


def skippable(changes):
    """The open stages a deal truly entered that its record passes on its way to a later one.

    A record that ends at an open stage (a dead lead left open) cannot skip that last one.
    """
    true = sorted(
        (c for c in changes if c["true_entered_at"] and c["crm_stage"] in OPEN_AFTER_CREATION),
        key=lambda c: c["true_entered_at"],
    )
    closed = any(c["crm_stage"] in CLOSED and c["recorded_entered_at"] for c in changes)
    return true if closed else true[:-1]


@pytest.mark.parametrize(
    ("setting", "share"),
    [
        ("middle", 0.50),
        ("recording.skips_a_stage@low", 0.35),
        ("recording.skips_a_stage@high", 0.65),
    ],
)
def test_the_profiles_share_of_records_skip_a_stage(generated, setting, share):
    passing = [s for s in map(skippable, history_by_deal(generated(setting)).values()) if s]
    skipping = [s for s in passing if any(not c["recorded_entered_at"] for c in s)]
    assert len(skipping) / len(passing) == pytest.approx(share, abs=0.04)


def moved_back(changes):
    """The recorded changes with no true event behind them: a deal moved back and on again."""
    return [c for c in changes if not c["true_entered_at"]]


def can_move_back(changes):
    return any(
        c["true_entered_at"] and c["recorded_entered_at"] and c["crm_stage"] in OPEN_AFTER_CREATION
        for c in changes
    )


@pytest.mark.parametrize(
    ("setting", "share", "tolerance"),
    [
        ("middle", 0.05, 0.015),
        ("recording.backward_move@low", 0.02, 0.01),
        ("recording.backward_move@high", 0.10, 0.021),
    ],
)
def test_the_profiles_share_of_deals_move_backward(generated, setting, share, tolerance):
    deals = [c for c in history_by_deal(generated(setting)).values() if can_move_back(c)]
    backward = [c for c in deals if moved_back(c)]
    assert len(backward) / len(deals) == pytest.approx(share, abs=tolerance)


def test_moving_back_overwrites_the_date_entered_of_the_stage_entered_again(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    overwritten = 0
    for deal_id, changes in history_by_deal(middle).items():
        for again in moved_back(changes):
            first = next(c for c in changes if c["crm_stage"] == again["crm_stage"])
            assert first["recorded_entered_at"] < again["recorded_entered_at"]
            if again["recorded_entered_at"] < EXPORT:
                shown = deals[deal_id][entered(again["crm_stage"])]
                assert shown >= again["recorded_entered_at"] > first["recorded_entered_at"]
                overwritten += 1
    assert overwritten


WON = {"Deposit Paid", "Travelled", "Cancelled"}


@pytest.mark.parametrize(
    ("setting", "share", "tolerance"),
    [
        ("middle", 0.10, 0.06),
        ("recording.won_without_amount@low", 0.02, 0.03),
        ("recording.won_without_amount@high", 0.30, 0.09),
    ],
)
def test_the_profiles_share_of_won_deals_have_no_amount(generated, setting, share, tolerance):
    won = [d for d in rows(generated(setting) / DEALS) if d["Deal Stage"] in WON]
    assert sum(not d["Amount"] for d in won) / len(won) == pytest.approx(share, abs=tolerance)


MEANINGS = {
    r["recorded"]: r["meaning"] for r in profile.load(PROFILE)["loss"]["reasons"]["recorded"]
}


def lost_with_truth(folder):
    truth = {r["deal_record_id"]: r for r in rows(folder / TRUTH)}
    deals = [d for d in rows(folder / DEALS) if d["Deal Stage"] == "Lost"]
    return [(d, truth[d["Record ID"]]) for d in deals]


@pytest.mark.parametrize(
    ("setting", "share"),
    [("middle", 0.35), ("loss.blank_reason@low", 0.15), ("loss.blank_reason@high", 0.50)],
)
def test_the_profiles_share_of_lost_deals_have_no_reason(generated, setting, share):
    lost = lost_with_truth(generated(setting))
    blank = sum(not deal["Closed Lost Reason"] for deal, _ in lost)
    assert blank / len(lost) == pytest.approx(share, abs=0.04)


@pytest.mark.parametrize(
    ("setting", "share"),
    [
        ("middle", 0.40),
        ("loss.recorded_differs_from_truth@low", 0.20),
        ("loss.recorded_differs_from_truth@high", 0.60),
    ],
)
def test_the_profiles_share_of_recorded_reasons_differ_from_the_true_one(generated, setting, share):
    given = [(d, t) for d, t in lost_with_truth(generated(setting)) if d["Closed Lost Reason"]]
    differs = sum(MEANINGS[d["Closed Lost Reason"]] != t["true_loss_reason"] for d, t in given)
    assert differs / len(given) == pytest.approx(share, abs=0.05)


def test_every_lost_lead_and_no_other_has_a_true_loss_reason_drawn_from_the_profile(middle):
    lost = {c["deal_record_id"] for c in rows(middle / STAGES) if c["crm_stage"] == "Lost"}
    truth = rows(middle / TRUTH)
    for row in truth:
        assert bool(row["true_loss_reason"]) == (row["deal_record_id"] in lost), row
    reasons = Counter(r["true_loss_reason"] for r in truth if r["true_loss_reason"])
    # The middle shares sum to 1.15, so each is scaled down to its part of the total.
    for reason, share in [
        ("could_not_reach_them", 0.35),
        ("price", 0.40),
        ("timing", 0.25),
        ("never_a_real_buyer", 0.15),
    ]:
        assert reasons[reason] / reasons.total() == pytest.approx(share / 1.15, abs=0.03)


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
