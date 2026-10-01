import math
import re
import statistics
from collections import Counter
from datetime import date
from pathlib import Path
from random import Random

import pytest

from emva_sim import form, leads, profile
from emva_sim.leads import DatesGiven, Market

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
# The standard error of a sample median is about this times the spread over the root of n (for a
# normal spread, as the logs of a lognormal draw are): sqrt(pi / 2).
MEDIAN_SE = math.sqrt(math.pi / 2)


def assert_share(found, expected, n):
    """A share within 3 standard errors of expected, at n leads."""
    assert abs(found - expected) <= 3 * math.sqrt(expected * (1 - expected) / n), (found, expected)


@pytest.fixture(scope="module")
def drawn():
    p = profile.resolve(profile.load(PROFILE), "middle")
    return leads.draw_leads(Random(1), p, date(2024, 1, 1), date(2024, 3, 31))


def test_the_profiles_price_is_the_season_average(drawn):
    # Luxury averages $1,300 a night; peak (4 of 12 travel months) pays 1.4 times low season:
    # low = 1300 / (8/12 + 4/12 x 1.4) = 1147.06, peak = 1.4 x low = 1605.88.
    luxury = [lead for lead in drawn if lead.style == "luxury"]
    peak_months = middle()["season"]["peak_months"]
    peak = [
        lead.price_per_person_per_night for lead in luxury if lead.travel_at.month in peak_months
    ]
    low = [
        lead.price_per_person_per_night
        for lead in luxury
        if lead.travel_at.month not in peak_months
    ]
    assert peak and low
    assert peak == pytest.approx([1605.88] * len(peak), abs=0.01)
    assert low == pytest.approx([1147.06] * len(low), abs=0.01)


def test_the_lead_draws_read_only_the_effects_that_shape_a_lead():
    # The proxy trap shifts the draws themselves and text_commitment's share sets a hidden flag;
    # every other effect acts only on the propensity.
    p = profile.resolve(profile.load(PROFILE), "middle")
    p["effects"] = {name: p["effects"][name] for name in ("proxy_trap_country", "text_commitment")}
    assert leads.draw_leads(Random(1), p, date(2024, 1, 1), date(2024, 1, 2))


def test_answers_come_from_the_options_numbers_and_flags_not_their_wording():
    p = profile.resolve(profile.load(PROFILE), "middle")
    relabelled = {}
    for field in p["form"]["fields"]:
        for i, option in enumerate(field.get("options", [])):
            option["label"] = f"{field['role']} option {i}"
            relabelled.setdefault(field["label"], set()).add(option["label"])
    p["exports"]["deal_properties"] = []
    drawn = leads.draw_leads(Random(1), p, date(2024, 1, 1), date(2024, 1, 31))
    for lead in drawn:
        for label, options in relabelled.items():
            answer = lead.answers[label]
            assert answer == "" or set(answer.split(";")) <= options, (label, answer)


def test_children_come_only_with_families(drawn):
    with_children = [lead for lead in drawn if lead.children]
    assert_share(len(with_children) / len(drawn), 0.28, len(drawn))


def middle():
    return profile.resolve(profile.load(PROFILE), "middle")


def draw(p, days=31):
    return leads.draw_leads(Random(1), p, date(2024, 1, 1), date(2024, 1, days))


def answers(drawn_leads, label):
    return [lead.answers[label] for lead in drawn_leads]


def share(values, wanted):
    return sum(v == wanted for v in values) / len(values)


def test_adults_per_party_and_childrens_ages_come_from_the_profile():
    p = middle()
    p["form"]["party_size"]["adults"]["family"] = 1
    p["form"]["party_size"]["child_ages"] = {"min": 5, "max": 6}
    drawn_leads = draw(p)
    families = [lead for lead in drawn_leads if lead.children]
    assert families and all(lead.adults == 1 for lead in families)
    ages = {a for lead in families for a in lead.answers["Ages of children"].split(", ")}
    assert ages == {"5", "6"}


@pytest.mark.parametrize(
    ("label", "answer", "expected"),
    [
        ("Sign me up for the newsletter", "Yes", 0.40),
        ("Are your dates flexible?", "Fixed", 0.30),
        ("Are your dates flexible?", "Flexible", 0.50),
        ("Have you travelled with us before?", "I have enquired before", 0.97 * 0.08),
    ],
)
def test_optional_answers_follow_the_profiles_shares(drawn, label, answer, expected):
    assert_share(share(answers(drawn, label), answer), expected, len(drawn))


def test_titles_follow_the_profiles_mix_including_mx():
    p = middle()
    p["people"]["titles"] = {"female": {"mx": 1.0}, "male": {"mx": 1.0}}
    assert set(answers(draw(p, days=2), "Title")) == {"Mx"}
    assert "Mx" in answers(draw(middle()), "Title")


def test_a_market_country_brings_its_own_phone_format():
    p = middle()
    p["markets"]["groups"]["b"]["countries"] = [{"name": "Ireland", "phones": ["+353 1 ### 0000"]}]
    p["form"]["answers"]["gives_phone_when_optional"] = 1.0
    irish = [lead for lead in draw(p, days=2) if lead.country == "Ireland"]
    assert irish
    assert all(re.fullmatch(r"\+353 1 \d{3} 0000", lead.answers["Phone"]) for lead in irish)


def booking_lead_time_months(lead):
    days = (lead.travel_at - lead.submitted_at).total_seconds() / 86400 - lead.cycle_days
    return days / leads.DAYS_PER_MONTH


def budget_to_style_price(p, lead):
    return lead.budget_per_person_per_night / p["deal"]["price_per_person_per_night"][lead.style]


@pytest.fixture(scope="module")
def year_of_leads():
    p = middle()
    return p, leads.draw_leads(Random(2), p, date(2024, 1, 1), date(2024, 12, 31))


def year_at(setting):
    p = profile.resolve(profile.load(PROFILE), setting)
    return p, leads.draw_leads(Random(2), p, date(2024, 1, 1), date(2024, 12, 31))


def assert_market_ratio(p, drawn, measure, sigma, expected):
    """Market A's median over market B's, within 3 standard errors of expected (log scale)."""
    by_group = {g: [lead for lead in drawn if lead.market_group == g] for g in Market}
    medians = {g: statistics.median(measure(p, x) for x in by_group[g]) for g in Market}
    found = math.log(medians[Market.A] / medians[Market.B])
    se = MEDIAN_SE * sigma * math.sqrt(sum(1 / len(group) for group in by_group.values()))
    assert abs(found - math.log(expected)) <= 3 * se, (math.exp(found), expected)


def assert_markets_apart(p, drawn, budget, lead_time):
    process = p["process"]
    sigma = p["form"]["answers"]["budget_sigma"]
    assert_market_ratio(p, drawn, budget_to_style_price, sigma, budget)
    sigma = process["booking_lead_time_sigma"]
    assert_market_ratio(p, drawn, lead_time_months, sigma, lead_time)


def lead_time_months(_, lead):
    return booking_lead_time_months(lead)


TRAP = "effects.proxy_trap_country"


@pytest.mark.parametrize(
    ("setting", "budget", "lead_time"),
    [
        (f"{TRAP}.budget_multiplier@low", 1.3, 1.5),
        (f"{TRAP}.budget_multiplier@high", 2.0, 1.5),
        (f"{TRAP}.lead_time_multiplier@low", 1.6, 1.2),
        (f"{TRAP}.lead_time_multiplier@high", 1.6, 2.0),
    ],
)
def test_the_trap_moves_the_markets_apart_by_its_multipliers_at_each_end(
    setting, budget, lead_time
):
    assert_markets_apart(*year_at(setting), budget, lead_time)


@pytest.mark.parametrize(("end", "share"), [("low", 0.10), ("high", 0.30)])
def test_the_text_commitment_share_follows_its_ends(end, share):
    _, drawn = year_at(f"effects.text_commitment.share_of_leads@{end}")
    assert_share(sum(lead.text_commitment for lead in drawn) / len(drawn), share, len(drawn))


def test_market_a_states_budgets_1_6_times_and_books_1_5_times_as_far_ahead_as_market_b(
    year_of_leads,
):
    # effects.proxy_trap_country at its middle: budget median x 1.6, lead time median x 1.5.
    assert_markets_apart(*year_of_leads, 1.6, 1.5)


def shares(values):
    counted = Counter(values)
    return {key: n / sum(counted.values()) for key, n in counted.items()}


def test_a_fifth_of_messages_are_blank_or_a_token(year_of_leads):
    # form.message.blank_or_token at its middle.
    p, drawn = year_of_leads
    token = p["form"]["message"]["shape"]["token_words_at_most"]
    blank = sum(lead.message_words <= token for lead in drawn) / len(drawn)
    assert_share(blank, 0.20, len(drawn))


def test_dreamers_write_long_name_many_countries_and_state_no_budget(year_of_leads):
    # form.message.dreamer_share at its middle: 5 in 100 leads.
    p, drawn = year_of_leads
    shape = p["form"]["message"]["shape"]
    dreamers = [
        lead
        for lead in drawn
        if lead.message_words > shape["dreamer_over_words"]
        and len(lead.destinations) > shape["dreamer_over_countries"]
        and not lead.states_budget
    ]
    assert_share(len(dreamers) / len(drawn), 0.05, len(drawn))


def test_most_messages_run_near_the_profiles_median_length(year_of_leads):
    # Messages that are neither blank, a token nor a dreamer's: lognormal, median 45 words.
    p, drawn = year_of_leads
    message = p["form"]["message"]
    shape = message["shape"]
    written = [
        lead.message_words
        for lead in drawn
        if shape["token_words_at_most"] < lead.message_words <= shape["dreamer_over_words"]
    ]
    se = MEDIAN_SE * message["words_sigma"] / math.sqrt(len(written))
    assert abs(math.log(statistics.median(written) / 45)) <= 3 * se


@pytest.mark.parametrize(("flag", "share"), [("text_commitment", 0.20), ("real_buyer", 0.50)])
def test_the_hidden_text_flags_follow_their_shares(year_of_leads, flag, share):
    _, drawn = year_of_leads
    assert_share(sum(getattr(lead, flag) for lead in drawn) / len(drawn), share, len(drawn))


def test_the_answers_show_the_leads_hidden_choices(year_of_leads):
    p, drawn = year_of_leads
    unsure = form.unsure(p, "destinations")
    for lead in drawn:
        assert bool(lead.answers["Phone"]) == lead.gives_phone
        budget = lead.answers["Budget per person (excluding international flights)"]
        assert bool(budget) == lead.states_budget
        named = lead.answers["Where would you like to go?"]
        assert named == (";".join(lead.destinations) if lead.destinations else unsure)
    n = len(drawn)
    assert_share(sum(lead.states_budget for lead in drawn) / n, 0.45, n)
    found = shares(lead.dates_given for lead in drawn)
    assert_share(found[DatesGiven.EXACT], 0.25, n)
    assert_share(found[DatesGiven.MONTH], 0.75 * 0.6, n)
    assert_share(found[DatesGiven.YEAR], 0.75 * 0.4 * 0.5, n)
    assert_share(found[DatesGiven.NOT_SURE], 0.75 * 0.4 * 0.5, n)


def test_pooled_over_both_markets_budgets_and_lead_times_keep_the_profiles_medians(year_of_leads):
    # Half the leads in each market: the pooled medians are the profile's own middles,
    # 1.0 x the style's price and 6 months from deposit to travel.
    # The pooled spread in logs is each market's sigma widened by the markets' half-gap.
    p, drawn = year_of_leads
    trap = p["effects"]["proxy_trap_country"]
    for measure, sigma, gap, expected in [
        (budget_to_style_price, p["form"]["answers"]["budget_sigma"], "budget_multiplier", 1.0),
        (lead_time_months, p["process"]["booking_lead_time_sigma"], "lead_time_multiplier", 6),
    ]:
        pooled = statistics.median(measure(p, x) for x in drawn)
        spread = math.hypot(sigma, math.log(trap[gap]) / 2)
        se = MEDIAN_SE * spread / math.sqrt(len(drawn))
        assert abs(math.log(pooled / expected)) <= 3 * se, (pooled, expected)
