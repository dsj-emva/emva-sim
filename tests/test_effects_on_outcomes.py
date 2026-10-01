"""Each planted effect is present in the Outcomes at the size the profile says, on simulated data.

For each effect, contacted leads in its group against its reference group, by what the lead is
(never by the term itself), in strata where every other term is held fixed. The measured odds ratio
of winning (Mantel-Haenszel) must lie within 3 standard errors of the profile's middle, and each
comparison must be precise enough to mean something: a standard error of at most 0.07 on the log
odds ratio. Both rules were written before any result was seen.

The middle sample is 150,000 leads at the middle. Effects whose groups win too rarely there for
that precision (the party size, the repeat client's softened floor, the price rise, a budget under
half the floor, a short lead time) are measured on a second sample of 72,000 leads with every
effect size still at its middle but more leads in those groups and more wins: more repeat clients,
larger friends' parties, more budgets and exact dates stated, a lower and wider budget spread,
and a higher reply and deposit rate.
"""

import math
from datetime import datetime

import pytest
from conftest import large_sample
from odds import log_odds, mantel_haenszel, rest_without, stratum

MAX_SE = 0.07
PEAK = (7, 8, 9, 10)
RISE = datetime(2025, 2, 1)
PRICE = {"comfortable": 550, "luxury": 1300, "ultra_luxury": 3000}


@pytest.fixture(scope="module")
def rich_sample():
    return large_sample(
        "middle",
        3000,
        seed=2,
        **{
            "form.answers.travelled_before": 0.30,
            "form.party_mix.friends": 0.40,
            "form.party_size.friends_adults": 7.0,
            "form.answers.states_budget": 0.90,
            "form.answers.states_exact_dates": 0.60,
            "form.answers.budget_to_style_price": 0.6,
            "form.answers.budget_sigma": 1.0,
            "process.transition.engaged": 0.8,
            "process.transition.won": 0.6,
        },
    )


def lead(row):
    return row["lead"]


def old_floor(row):
    return 0.7 * PRICE[lead(row).style]


def floor_share(row):
    """The stated budget as a share of the floor in force when the lead was submitted."""
    risen = 1.1 if lead(row).submitted_at >= RISE else 1.0
    return lead(row).budget_per_person_per_night / (old_floor(row) * risen)


def stated(row):
    return lead(row).states_budget


def new_client(row):
    return not lead(row).repeat_client


def peak(row):
    return lead(row).travel_at.month in PEAK


def ahead(row):
    return lead(row).months_ahead


def dated(row):
    return lead(row).dates_given not in ("year", "not_sure")


def hours_to_first_attempt(row):
    path = row["path"]
    return (path.stage_times["Contact attempted"] - lead(row).submitted_at).total_seconds() / 3600


def high_quality(row):
    return row["high_quality"] == "yes"


def at_floor(row):
    return stated(row) and new_client(row) and floor_share(row) >= 1


def lead_time_reference(row):
    if not dated(row):
        return False
    return (peak(row) and 6 <= ahead(row) <= 14) or (not peak(row) and 4 <= ahead(row) <= 8)


def written(lo, hi):
    return lambda row: lo <= lead(row).message_words <= hi


def dreamer(row):
    x = lead(row)
    return x.message_words > 400 and len(x.destinations) > 3 and not x.states_budget


def source(name):
    return lambda row: lead(row).traffic_source == name


def after_rise_stated(row):
    return stated(row) and lead(row).submitted_at >= RISE


def share_of_old_floor(row):
    return lead(row).budget_per_person_per_night / old_floor(row)


# (name, sample, profile odds ratio at the middle, group, reference, term held out of the strata)
CASES = [
    (
        "budget under half the floor",
        "rich",
        0.10,
        lambda r: stated(r) and new_client(r) and floor_share(r) < 0.5,
        at_floor,
        "budget_floor",
    ),
    (
        "budget from half the floor to the floor",
        "middle",
        0.50,
        lambda r: stated(r) and new_client(r) and 0.5 <= floor_share(r) < 1,
        at_floor,
        "budget_floor",
    ),
    (
        "repeat client's budget below the floor (softened: 0.5 ** 0.5)",
        "rich",
        0.50**0.5,
        lambda r: stated(r) and not new_client(r) and 0.5 <= floor_share(r) < 1,
        lambda r: stated(r) and not new_client(r) and floor_share(r) >= 1,
        "budget_floor",
    ),
    (
        "no budget stated",
        "middle",
        0.70,
        lambda r: not stated(r),
        lambda r: stated(r) and floor_share(r) >= 1,
        "no_budget",
    ),
    (
        "peak travel under 4 months ahead",
        "rich",
        0.40,
        lambda r: dated(r) and peak(r) and ahead(r) < 4,
        lead_time_reference,
        "lead_time_by_season",
    ),
    (
        "off-peak travel under 4 months ahead",
        "rich",
        1.0,
        lambda r: dated(r) and not peak(r) and ahead(r) < 4,
        lead_time_reference,
        "lead_time_by_season",
    ),
    (
        "travel over 18 months ahead or not sure",
        "rich",
        0.60,
        lambda r: not dated(r) or ahead(r) > 18,
        lead_time_reference,
        "lead_time_by_season",
    ),
    (
        "dates given as a month",
        "middle",
        0.90,
        lambda r: lead(r).dates_given == "month",
        lambda r: lead(r).dates_given == "exact",
        "date_specificity",
    ),
    (
        "no dates given",
        "middle",
        0.55,
        lambda r: lead(r).dates_given in ("year", "not_sure"),
        lambda r: lead(r).dates_given == "exact",
        "date_specificity",
    ),
    ("referral", "middle", 4.0, source("referral"), source("paid_search"), "lead_source"),
    ("paid social", "middle", 0.6, source("paid_social"), source("paid_search"), "lead_source"),
    ("organic search", "middle", 1.4, source("organic"), source("paid_search"), "lead_source"),
    (
        "repeat client",
        "middle",
        6.0,
        lambda r: lead(r).repeat_client,
        new_client,
        "repeat_client",
    ),
    (
        "high quality, first attempt within 1 hour",
        "middle",
        4.0,
        lambda r: high_quality(r) and hours_to_first_attempt(r) <= 1,
        lambda r: high_quality(r) and hours_to_first_attempt(r) > 24,
        "response_speed_by_quality",
    ),
    (
        "low quality, first attempt within 1 hour",
        "middle",
        1.1,
        lambda r: not high_quality(r) and hours_to_first_attempt(r) <= 1,
        lambda r: not high_quality(r) and hours_to_first_attempt(r) > 24,
        "response_speed_by_quality",
    ),
    (
        "message under 15 words",
        "middle",
        0.60,
        written(0, 14),
        written(40, 200),
        "message_length",
    ),
    ("dreamer", "middle", 0.75, dreamer, written(40, 200), "message_length"),
    (
        "party over 6",
        "rich",
        0.70,
        lambda r: lead(r).party_size > 6,
        lambda r: lead(r).party_size == 2,
        "party_size",
    ),
    (
        "phone given",
        "middle",
        1.5,
        lambda r: lead(r).gives_phone,
        lambda r: not lead(r).gives_phone,
        "phone_given",
    ),
    (
        "after the price rise, a budget just above the new floor",
        "rich",
        0.75,
        lambda r: after_rise_stated(r) and floor_share(r) >= 1 and share_of_old_floor(r) < 1.3,
        lambda r: after_rise_stated(r) and share_of_old_floor(r) >= 1.5,
        "price_rise",
    ),
    (
        "commitment shown in the text",
        "middle",
        2.5,
        lambda r: lead(r).text_commitment,
        lambda r: not lead(r).text_commitment,
        "text_commitment",
    ),
    (
        "a real buyer, as the notes show",
        "middle",
        3.5,
        lambda r: lead(r).real_buyer,
        lambda r: not lead(r).real_buyer,
        "notes_real_buyer",
    ),
]


@pytest.fixture(scope="module")
def samples(middle_sample, rich_sample):
    return {"middle": middle_sample, "rich": rich_sample}


def measured(rows, group, reference, term):
    return mantel_haenszel(rows, group, reference, rest_without(term))


@pytest.mark.parametrize(
    ("name", "sample", "odds_ratio", "group", "reference", "term"), CASES, ids=[c[0] for c in CASES]
)
def test_the_outcomes_carry_each_effect_at_the_profiles_size(
    samples, name, sample, odds_ratio, group, reference, term
):
    log_or, se = measured(samples[sample], group, reference, term)
    assert se <= MAX_SE, (name, se)
    assert abs(log_or - math.log(odds_ratio)) <= 3 * se, (name, math.exp(log_or), odds_ratio)


def contrast(rows, first, second):
    """The difference of two measured log odds ratios and its standard error."""
    (a, a_se), (b, b_se) = measured(rows, *first), measured(rows, *second)
    return a - b, math.hypot(a_se, b_se)


def case(name):
    _, _, _, group, reference, term = next(c for c in CASES if c[0] == name)
    return group, reference, term


def test_season_changes_what_a_short_lead_time_does(rich_sample):
    # Interaction: under 4 months ahead costs a peak trip 0.40 and an off-peak trip nothing.
    difference, se = contrast(
        rich_sample,
        case("peak travel under 4 months ahead"),
        case("off-peak travel under 4 months ahead"),
    )
    assert difference < -3 * se
    assert abs(difference - math.log(0.40)) <= 3 * se


def test_quality_changes_what_a_quick_first_attempt_does(middle_sample):
    # Interaction: within an hour lifts a high-quality lead 4.0 and a low-quality one 1.1.
    difference, se = contrast(
        middle_sample,
        case("high quality, first attempt within 1 hour"),
        case("low quality, first attempt within 1 hour"),
    )
    assert difference > 3 * se
    assert abs(difference - math.log(4.0 / 1.1)) <= 3 * se


@pytest.mark.parametrize(
    ("sample", "short", "long"),
    [
        ("middle", "message under 15 words", "dreamer"),
        ("rich", "peak travel under 4 months ahead", "travel over 18 months ahead or not sure"),
    ],
)
def test_the_middle_does_best_with_both_ends_worse(samples, sample, short, long):
    # Inverted U: both ends win less often than the middle band, each clearly.
    for name in (short, long):
        log_or, se = measured(samples[sample], *case(name))
        assert log_or < -3 * se, name


def market_a(row):
    return row["market_group"] == "A"


def market_b(row):
    return row["market_group"] == "B"


def test_the_market_predicts_the_outcome_on_its_own(middle_sample):
    # Only through the budget floor (stated by 45%, felt only below the floor) at the middle: an
    # odds ratio near 1.1, but clear of 1 by more than 3 standard errors.
    log_or, se = mantel_haenszel(middle_sample, market_a, market_b)
    assert log_or > 3 * se, math.exp(log_or)


def test_the_market_has_no_effect_once_the_leads_terms_are_held(middle_sample):
    # Strata by the whole win log-odds: budget, lead time, season and every other term held.
    log_or, se = mantel_haenszel(middle_sample, market_a, market_b, lambda r: stratum(log_odds(r)))
    assert se <= MAX_SE
    assert abs(log_or) <= 3 * se, math.exp(log_or)


def test_the_market_has_no_term_of_its_own():
    from emva_sim.dataset import HIDDEN_TRUTH_COLUMNS

    assert not [c for c in HIDDEN_TRUTH_COLUMNS if c.startswith("term_") and "market" in c]
