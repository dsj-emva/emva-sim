"""Each planted effect is a named term on a lead's win log-odds: log of the profile's odds ratio.

Hand-made leads at the edges of each effect's groups, at the middle and at each end of the effect's
range (that range at its end, every other at its middle). Expected values are the profile's own
numbers.
"""

import math
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

import pytest

from emva_sim import leads, profile
from emva_sim.effects import Effects

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
RAW = profile.load(PROFILE)
HISTORY_START = date(2024, 1, 1)
# Month 14 of a history that starts in January 2024.
RISE = datetime(2025, 2, 1)
# Luxury's middle price is $1,300 a night; the floor is 0.7 of it.
LUXURY_FLOOR = 0.7 * 1300


def resolved(setting="middle"):
    return profile.resolve(RAW, setting)


def at(name, end):
    """A range's number at an end, read from the profile as written."""
    node = RAW
    for key in name.split("."):
        node = node[key]
    return node[end]


def reference_lead():
    """A lead in every effect's reference group: each term is zero."""
    drawn = leads.draw_leads(Random(1), resolved(), date(2024, 1, 1), date(2024, 1, 1))[0]
    submitted = datetime(2024, 6, 1, 12)
    return replace(
        drawn,
        submitted_at=submitted,
        travel_at=submitted + timedelta(days=183),  # December: off-peak, 6 months ahead
        traffic_source="paid_search",
        repeat_client=False,
        style="luxury",
        adults=2,
        children=0,
        budget_per_person_per_night=1.2 * LUXURY_FLOOR,
        states_budget=True,
        gives_phone=False,
        dates_given="exact",
        destinations=("Kenya", "Tanzania"),
        message_words=100,
        message_specificity="very_specific",
        text_commitment=False,
        real_buyer=False,
    )


REFERENCE = reference_lead()


def terms(lead, setting="middle"):
    return Effects(resolved(setting), HISTORY_START).of_lead(lead)


def test_a_lead_in_every_reference_group_has_no_term():
    found = terms(REFERENCE)
    assert set(found) == {
        "budget_floor",
        "no_budget",
        "lead_time_by_season",
        "date_specificity",
        "lead_source",
        "repeat_client",
        "message_length",
        "party_size",
        "phone_given",
        "price_rise",
        "text_commitment",
        "notes_real_buyer",
    }
    assert set(found.values()) == {0.0}


def months_ahead(submitted, months):
    return {
        "submitted_at": submitted,
        "travel_at": submitted + timedelta(days=leads.DAYS_PER_MONTH * months),
    }


DREAMER = {
    "message_words": 500,
    "destinations": ("Kenya", "Tanzania", "Botswana", "Rwanda"),
    "states_budget": False,
}

# (range, changes that put the reference lead in the effect's group, the term that carries it)
CASES = [
    (
        "effects.budget_floor.below_half",
        {"budget_per_person_per_night": 0.49 * LUXURY_FLOOR},
        "budget_floor",
    ),
    (
        "effects.budget_floor.half_to_floor",
        {"budget_per_person_per_night": 0.5 * LUXURY_FLOOR},
        "budget_floor",
    ),
    (
        "effects.budget_floor.half_to_floor",
        {"budget_per_person_per_night": 0.99 * LUXURY_FLOOR},
        "budget_floor",
    ),
    ("effects.no_budget.odds_ratio", {"states_budget": False}, "no_budget"),
    (
        "effects.lead_time_by_season.peak_under_4_months",
        months_ahead(datetime(2024, 5, 1), 3.5),
        "lead_time_by_season",
    ),
    (
        "effects.lead_time_by_season.off_peak_under_4_months",
        months_ahead(datetime(2024, 1, 1), 2.5),
        "lead_time_by_season",
    ),
    (
        "effects.lead_time_by_season.over_18_months_or_unsure",
        months_ahead(datetime(2024, 1, 1), 19),
        "lead_time_by_season",
    ),
    (
        "effects.lead_time_by_season.over_18_months_or_unsure",
        {"dates_given": "not_sure"},
        "lead_time_by_season",
    ),
    (
        # a year only is "next year sometime" (what-predicts-a-booking.md §2): unsure too
        "effects.lead_time_by_season.over_18_months_or_unsure",
        {"dates_given": "year"},
        "lead_time_by_season",
    ),
    ("effects.date_specificity.month_only", {"dates_given": "month"}, "date_specificity"),
    ("effects.date_specificity.no_dates", {"dates_given": "year"}, "date_specificity"),
    ("effects.date_specificity.no_dates", {"dates_given": "not_sure"}, "date_specificity"),
    ("effects.lead_source.referral", {"traffic_source": "referral"}, "lead_source"),
    ("effects.lead_source.paid_social", {"traffic_source": "paid_social"}, "lead_source"),
    ("effects.lead_source.organic", {"traffic_source": "organic"}, "lead_source"),
    ("effects.repeat_client.odds_ratio", {"repeat_client": True}, "repeat_client"),
    ("effects.message_length.under_15_words", {"message_words": 14}, "message_length"),
    ("effects.message_length.under_15_words", {"message_words": 0}, "message_length"),
    ("effects.message_length.dreamer", DREAMER, "message_length"),
    ("effects.party_size.over_6", {"adults": 5, "children": 2}, "party_size"),
    ("effects.phone_given.odds_ratio_when_optional", {"gives_phone": True}, "phone_given"),
    (
        "effects.price_rise.near_floor_after",
        {
            "submitted_at": RISE,
            "travel_at": RISE + timedelta(days=183),
            "budget_per_person_per_night": 1.29 * LUXURY_FLOOR,
        },
        "price_rise",
    ),
    ("effects.text_commitment.odds_ratio", {"text_commitment": True}, "text_commitment"),
    ("effects.notes_real_buyer.odds_ratio", {"real_buyer": True}, "notes_real_buyer"),
]


@pytest.mark.parametrize("end", ["middle", "low", "high"])
@pytest.mark.parametrize(("name", "changes", "term"), CASES)
def test_a_lead_in_an_effects_group_carries_the_log_of_its_odds_ratio(name, changes, term, end):
    setting = "middle" if end == "middle" else f"{name}@{end}"
    found = terms(replace(REFERENCE, **changes), setting)
    assert found[term] == pytest.approx(math.log(at(name, end)))


def test_the_ends_of_every_effect_give_different_terms():
    for name, changes, term in CASES:
        low = terms(replace(REFERENCE, **changes), f"{name}@low")[term]
        high = terms(replace(REFERENCE, **changes), f"{name}@high")[term]
        assert low != high, name


@pytest.mark.parametrize(
    "changes",
    [
        {"budget_per_person_per_night": 1.0 * LUXURY_FLOOR},
        {"budget_per_person_per_night": 5.0 * LUXURY_FLOOR},
        months_ahead(datetime(2024, 1, 1), 18),  # travel in July, peak, 18 months ahead
        months_ahead(datetime(2024, 3, 1), 6),  # travel in September, peak, 6 months ahead
        months_ahead(datetime(2024, 4, 1), 4),  # travel in August, peak, 4 months ahead
        {"message_words": 15},
        {"message_words": 900},  # long, but names 2 countries and states a budget
        {"adults": 4, "children": 2},
        {"adults": 1},
        {"traffic_source": "paid_search", "dates_given": "exact"},
    ],
)
def test_the_edges_of_the_reference_groups_carry_no_term(changes):
    found = terms(replace(REFERENCE, **changes))
    assert set(found.values()) == {0.0}, found


def test_a_long_message_naming_3_countries_is_no_dreamer():
    found = terms(
        replace(REFERENCE, **{**DREAMER, "destinations": ("Kenya", "Tanzania", "Botswana")})
    )
    assert found["message_length"] == 0.0


def test_a_stated_budget_below_the_floor_takes_no_no_budget_term_and_a_missing_one_no_floor_term():
    below = terms(replace(REFERENCE, budget_per_person_per_night=0.4 * LUXURY_FLOOR))
    missing = terms(
        replace(REFERENCE, budget_per_person_per_night=0.4 * LUXURY_FLOOR, states_budget=False)
    )
    assert below["no_budget"] == 0.0 and below["budget_floor"] == pytest.approx(math.log(0.10))
    assert missing["budget_floor"] == 0.0 and missing["no_budget"] == pytest.approx(math.log(0.70))


def test_the_floor_follows_the_style_asked_for():
    # Comfortable's middle price is $550 a night: its floor is $385.
    comfortable = replace(REFERENCE, style="comfortable", budget_per_person_per_night=0.99 * 385)
    assert terms(comfortable)["budget_floor"] == pytest.approx(math.log(0.50))
    assert terms(replace(comfortable, budget_per_person_per_night=386))["budget_floor"] == 0.0


@pytest.mark.parametrize(
    ("setting", "kept"),
    [
        ("middle", 0.50),
        ("effects.repeat_client.floor_penalty_kept@low", 0.25),
        ("effects.repeat_client.floor_penalty_kept@high", 0.75),
    ],
)
def test_a_repeat_client_feels_only_the_kept_share_of_the_floor_penalty(setting, kept):
    repeat_below = replace(
        REFERENCE, repeat_client=True, budget_per_person_per_night=0.8 * LUXURY_FLOOR
    )
    found = terms(repeat_below, setting)
    assert found["budget_floor"] == pytest.approx(kept * math.log(0.50))
    assert found["repeat_client"] == pytest.approx(math.log(6.0))


def at_rise(budget_share_of_old_floor, submitted=RISE):
    return replace(
        REFERENCE,
        submitted_at=submitted,
        travel_at=submitted + timedelta(days=183),
        budget_per_person_per_night=budget_share_of_old_floor * LUXURY_FLOOR,
    )


def test_before_month_14_there_is_no_price_rise():
    before = terms(at_rise(1.05, submitted=RISE - timedelta(minutes=1)))
    assert before["budget_floor"] == 0.0 and before["price_rise"] == 0.0


@pytest.mark.parametrize(
    ("setting", "share_of_old_floor", "budget_floor", "price_rise"),
    [
        # the floor rises 10% at the middle: 1.05 x the old floor is now below it
        ("middle", 1.05, math.log(0.50), 0.0),
        ("middle", 1.11, 0.0, math.log(0.75)),
        ("middle", 1.31, 0.0, 0.0),
        # 5% at the low end, 20% at the high end
        ("effects.price_rise.floor_rise@low", 1.08, 0.0, math.log(0.75)),
        ("effects.price_rise.floor_rise@high", 1.08, math.log(0.50), 0.0),
        ("effects.price_rise.floor_rise@high", 1.21, 0.0, math.log(0.75)),
    ],
)
def test_after_month_14_the_floor_rises_and_budgets_just_above_it_lose_odds(
    setting, share_of_old_floor, budget_floor, price_rise
):
    found = terms(at_rise(share_of_old_floor), setting)
    assert found["budget_floor"] == pytest.approx(budget_floor)
    assert found["price_rise"] == pytest.approx(price_rise)


def test_a_missing_budget_takes_no_price_rise():
    assert terms(replace(at_rise(1.2), states_budget=False))["price_rise"] == 0.0


@pytest.mark.parametrize("end", ["middle", "low", "high"])
@pytest.mark.parametrize(
    ("quality", "name"),
    [(True, "high_quality_within_1h"), (False, "low_quality_within_1h")],
)
def test_a_first_attempt_within_an_hour_lifts_fully_and_one_after_a_day_not_at_all(
    quality, name, end
):
    full = f"effects.response_speed_by_quality.{name}"
    setting = "middle" if end == "middle" else f"{full}@{end}"
    p = resolved(setting)
    speed = p["effects"]["response_speed_by_quality"]
    quick, slow = speed["within_hours"], speed["no_lift_from_hours"]
    effects = Effects(p, HISTORY_START)
    lift = math.log(at(full, end))
    assert effects.response_speed(quick, quality) == pytest.approx(lift)
    assert effects.response_speed(quick / 10, quality) == pytest.approx(lift)
    assert effects.response_speed(slow, quality) == pytest.approx(0.0)
    assert effects.response_speed(slow * 2, quality) == 0.0


def test_a_speed_shape_the_generator_does_not_know_is_refused():
    p = resolved()
    p["effects"]["response_speed_by_quality"]["lift_between"] = "a step"
    with pytest.raises(ValueError, match="linear in log hours"):
        Effects(p, HISTORY_START)


@pytest.mark.parametrize("quality", [True, False])
def test_the_lift_of_a_quick_first_attempt_falls_linearly_in_log_hours(quality):
    # Ruled 2026-10-01 from "the quicker the contact after the form the better".
    p = resolved()
    speed = p["effects"]["response_speed_by_quality"]
    quick, slow = speed["within_hours"], speed["no_lift_from_hours"]
    effects = Effects(p, HISTORY_START)
    lift = effects.response_speed(quick, quality)
    for fraction in (0.25, 0.5, 0.75):
        hours = quick * (slow / quick) ** fraction
        assert effects.response_speed(hours, quality) == pytest.approx((1 - fraction) * lift)


def test_only_effects_visible_at_submission_count_towards_how_good_a_lead_looks():
    effects = Effects(resolved(), HISTORY_START)
    lead = replace(REFERENCE, real_buyer=True, traffic_source="referral")
    assert effects.apparent(effects.of_lead(lead)) == pytest.approx(math.log(4.0))
