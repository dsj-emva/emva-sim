"""How the sales team records each Lead's true path, on simulated data.

One fixed seed, six months of leads, exported long after the last one so nearly every stage change
is recorded before the export. Each rate is checked at the middle and at its range's low and high
ends, within STANDARD_ERRORS (conftest) at the size measured.
"""

import math
from collections import Counter, defaultdict
from datetime import date, datetime, time

import pytest
from conftest import (
    STAGES,
    TRUTH,
    assert_exponential_median,
    assert_rate,
    ends,
    genuine,
    number,
    raw,
    resolved,
    rows,
)

from emva_sim import dataset
from emva_sim.intake import RowKind

HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2025, 12, 31))
DEALS_ON = "export/deals-and-contacts-only/hubspot-crm-exports-safari-enquiries-%Y-%m-%d.csv"
DEALS = HISTORY.export.strftime(DEALS_ON)
EXPORT = "2025-12-31 00:00"
STAGE_LIST = raw()["pipeline"]["stages"]
CREATED = STAGE_LIST[0]["name"]
OPEN_AFTER_CREATION = {
    s["name"] for s in STAGE_LIST[1:] if "closed" not in s and "after_won" not in s
}
CLOSED = {s["name"]: s["closed"] for s in STAGE_LIST if "closed" in s}
WON = {s["name"] for s in STAGE_LIST if s.get("closed") == "won" or "after_won" in s}
MEANINGS = {r["recorded"]: r["meaning"] for r in raw()["loss"]["reasons"]["recorded"]}


def entered(stage):
    return f'Date entered "{stage} (Safari Enquiries)"'


@pytest.fixture(scope="module")
def generated(generate):
    return lambda setting: generate(setting, HISTORY)


@pytest.fixture(scope="module")
def middle(generated):
    return generated("middle")


def history_by_deal(folder):
    by_deal = defaultdict(list)
    for change in rows(folder / STAGES):
        by_deal[change["deal_record_id"]].append(change)
    return by_deal


def lead_histories(folder):
    leads = genuine(folder)
    return [changes for deal, changes in history_by_deal(folder).items() if deal in leads]


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


def moment(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


def days(start, end):
    return (moment(end) - moment(start)).total_seconds() / 86400


def hand_entered(folder):
    """Every recorded change but the deals' creation at their first stage."""
    changes = rows(folder / STAGES)
    return [c for c in changes if c["recorded_entered_at"] and c["crm_stage"] != CREATED]


def sharing(changes, at_least):
    """The changes whose timestamp at least this many changes have."""
    stamps = Counter(c["recorded_entered_at"] for c in changes)
    return [c for c in changes if stamps[c["recorded_entered_at"]] >= at_least]


REVIEW = raw()["recording"]["bulk_review"]


def at_the_review(change):
    # A deal moved through two stages at one review gets the second a minute after the first.
    at = moment(change["recorded_entered_at"])
    window = time(REVIEW["from_hour"]) <= at.time() <= time(REVIEW["to_hour"], 5)
    return at.strftime("%A") == REVIEW["weekday"] and window


def in_bulk(changes):
    """The changes made at a weekly review: in its hours, with a timestamp another one shares."""
    return [c for c in sharing(changes, 2) if at_the_review(c)]


def first_lags(folder):
    """Days from each deal's first true change after creation to when it was recorded.

    Changes made in bulk are left out: they wait for the weekly review instead. The first change
    is the one no earlier recorded change can push later.
    """
    bulk = {c["recorded_entered_at"] for c in in_bulk(hand_entered(folder))}
    lags = []
    for changes in lead_histories(folder):
        true = [c for c in changes if c["true_entered_at"] and c["crm_stage"] != CREATED]
        first = min(true, key=lambda c: c["true_entered_at"], default=None)
        if first and first["recorded_entered_at"] and first["recorded_entered_at"] not in bulk:
            lags.append(days(first["true_entered_at"], first["recorded_entered_at"]))
    return lags


@pytest.mark.parametrize("setting", ends("recording.lag_days_median"))
def test_stage_changes_are_recorded_late_by_the_profiles_median_lag(generated, setting):
    lags = first_lags(generated(setting))
    median = number(setting, "recording.lag_days_median")
    if median:
        assert_exponential_median(lags, median)
    else:
        # Pushed at most a minute behind the change recorded before it.
        assert max(lags) <= 1 / 1440 + 1e-9


@pytest.mark.parametrize("setting", ends("recording.bulk_update_share"))
def test_the_profiles_share_of_stage_changes_are_made_in_bulk(generated, setting):
    # Only while leads arrive is every review busy enough for its timestamp to be seen shared.
    changes = [c for c in hand_entered(generated(setting)) if c["recorded_entered_at"] < "2024-07"]
    assert_rate(len(in_bulk(changes)), len(changes), number(setting, "recording.bulk_update_share"))


def test_timestamps_many_changes_share_are_the_weekly_pipeline_reviews(middle):
    shared = sharing(hand_entered(middle), 3)
    assert shared
    assert all(at_the_review(change) for change in shared)


@pytest.mark.parametrize("setting", ends("recording.dead_left_open"))
def test_the_profiles_share_of_lost_leads_are_left_open_at_their_last_stage(generated, setting):
    folder = generated(setting)
    lost = [c for c in rows(folder / STAGES) if c["crm_stage"] == "Lost" and c["true_entered_at"]]
    left_open = [c for c in lost if not c["recorded_entered_at"]]
    assert_rate(len(left_open), len(lost), number(setting, "recording.dead_left_open"))
    deals = {d["Record ID"]: d for d in rows(folder / DEALS)}
    for change in left_open:
        deal = deals[change["deal_record_id"]]
        assert deal["Deal Stage"] != "Lost" and not deal["Closed Lost Reason"]


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


@pytest.mark.parametrize("setting", ends("recording.skips_a_stage"))
def test_the_profiles_share_of_records_skip_a_stage(generated, setting):
    passing = [s for s in map(skippable, lead_histories(generated(setting))) if s]
    skipping = [s for s in passing if any(not c["recorded_entered_at"] for c in s)]
    assert_rate(len(skipping), len(passing), number(setting, "recording.skips_a_stage"))


def moved_back(changes):
    """The recorded changes with no true event behind them: a deal moved back and on again."""
    return [c for c in changes if not c["true_entered_at"]]


def can_move_back(changes):
    return any(
        c["true_entered_at"] and c["recorded_entered_at"] and c["crm_stage"] in OPEN_AFTER_CREATION
        for c in changes
    )


@pytest.mark.parametrize("setting", ends("recording.backward_move"))
def test_the_profiles_share_of_deals_move_backward(generated, setting):
    deals = [c for c in lead_histories(generated(setting)) if can_move_back(c)]
    backward = [c for c in deals if moved_back(c)]
    assert_rate(len(backward), len(deals), number(setting, "recording.backward_move"))


def test_moving_back_overwrites_the_date_entered_of_the_stage_entered_again(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    overwritten = 0
    for changes in lead_histories(middle):
        deal_id = changes[0]["deal_record_id"]
        for again in moved_back(changes):
            first = next(c for c in changes if c["crm_stage"] == again["crm_stage"])
            assert first["recorded_entered_at"] < again["recorded_entered_at"]
            if again["recorded_entered_at"] < EXPORT:
                shown = deals[deal_id][entered(again["crm_stage"])]
                assert shown >= again["recorded_entered_at"] > first["recorded_entered_at"]
                overwritten += 1
    assert overwritten


@pytest.mark.parametrize("setting", ends("recording.won_without_amount"))
def test_the_profiles_share_of_won_deals_have_no_amount(generated, setting):
    won = [d for d in rows(generated(setting) / DEALS) if d["Deal Stage"] in WON]
    blank = sum(not d["Amount"] for d in won)
    assert_rate(blank, len(won), number(setting, "recording.won_without_amount"))


def lost_with_truth(folder):
    truth = {r["deal_record_id"]: r for r in rows(folder / TRUTH) if r["row_kind"] == RowKind.LEAD}
    deals = [
        d for d in rows(folder / DEALS) if d["Deal Stage"] == "Lost" and d["Record ID"] in truth
    ]
    return [(d, truth[d["Record ID"]]) for d in deals]


@pytest.mark.parametrize("setting", ends("loss.blank_reason"))
def test_the_profiles_share_of_lost_deals_have_no_reason(generated, setting):
    lost = lost_with_truth(generated(setting))
    blank = sum(not deal["Closed Lost Reason"] for deal, _ in lost)
    assert_rate(blank, len(lost), number(setting, "loss.blank_reason"))


@pytest.mark.parametrize("setting", ends("loss.recorded_differs_from_truth"))
def test_the_profiles_share_of_recorded_reasons_differ_from_the_true_one(generated, setting):
    given = [(d, t) for d, t in lost_with_truth(generated(setting)) if d["Closed Lost Reason"]]
    differs = sum(MEANINGS[d["Closed Lost Reason"]] != t["true_loss_reason"] for d, t in given)
    assert_rate(differs, len(given), number(setting, "loss.recorded_differs_from_truth"))


def test_every_lost_lead_and_no_other_has_a_true_loss_reason(middle):
    lost = {
        c["deal_record_id"]
        for c in rows(middle / STAGES)
        if c["crm_stage"] == "Lost" and c["true_entered_at"]
    }
    for row in rows(middle / TRUTH):
        assert bool(row["true_loss_reason"]) == (row["deal_record_id"] in lost), row


def true_reasons(folder, lost_before_engaged):
    """The true loss reasons of the Leads lost before Engaged, or of those lost at it or later."""
    return Counter(
        r["true_loss_reason"]
        for r in rows(folder / TRUTH)
        if r["true_loss_reason"]
        and (r["reached_stage"] == "Contact attempted") == lost_before_engaged
    )


@pytest.mark.parametrize("setting", ends("loss.reasons.could_not_reach_them"))
def test_a_lead_lost_before_engaged_truly_could_not_be_reached_or_was_never_a_buyer(
    generated, setting
):
    reasons = true_reasons(generated(setting), lost_before_engaged=True)
    assert set(reasons) == {"could_not_reach_them", "never_a_real_buyer"}
    share = number(setting, "loss.reasons.could_not_reach_them")
    assert_rate(reasons["could_not_reach_them"], reasons.total(), share)


def test_a_lead_lost_later_has_a_true_reason_by_the_profiles_weights(middle):
    reasons = true_reasons(middle, lost_before_engaged=False)
    later = set(MEANINGS.values()) - {"could_not_reach_them"}
    assert set(reasons) == later
    weights = {m: number("middle", f"loss.reasons.{m}") for m in later}
    for reason, weight in weights.items():
        assert_rate(reasons[reason], reasons.total(), weight / sum(weights.values()))


def test_a_change_recorded_after_the_export_date_is_not_shown_though_it_happened_before(
    generate,
):
    soon = dataset.History(start=date(2024, 1, 1), end=date(2024, 3, 31), export=date(2024, 4, 3))
    folder = generate("middle", soon)
    deals = {d["Record ID"]: d for d in rows(folder / soon.export.strftime(DEALS_ON))}
    late = [
        c
        for c in rows(folder / STAGES)
        if c["true_entered_at"] and c["true_entered_at"] < "2024-04-03" <= c["recorded_entered_at"]
    ]
    assert late
    for change in late:
        shown = deals[change["deal_record_id"]][entered(change["crm_stage"])]
        assert shown < "2024-04-03", change


def test_close_date_follows_the_recorded_close_not_the_true_one(middle):
    by_deal = history_by_deal(middle)
    closed = [d for d in rows(middle / DEALS) if d["Deal Stage"] in CLOSED]
    true_closes = later = 0
    for deal in closed:
        stage = deal["Deal Stage"]
        assert deal["Close Date"] == deal[entered(stage)], deal["Record ID"]
        change = next(c for c in by_deal[deal["Record ID"]] if c["crm_stage"] == stage)
        if change["true_entered_at"]:
            assert change["recorded_entered_at"] >= change["true_entered_at"]
            true_closes += 1
            later += change["recorded_entered_at"] > change["true_entered_at"]
    # A close keeps its true minute only if entered by hand less than a minute after it.
    p = resolved("middle")["recording"]
    within_a_minute = 1 - math.exp(-math.log(2) / p["lag_days_median"] / 1440)
    assert_rate(later, true_closes, 1 - (1 - p["bulk_update_share"]) * within_a_minute)
