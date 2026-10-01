"""The enquiry message each Lead writes, on simulated data.

A year of Leads, each message written from the phrase bank with the fake model's cached variations
(fake_model). Rates are checked within STANDARD_ERRORS (conftest) at the size measured.
"""

import re
from collections import Counter
from dataclasses import replace
from datetime import date
from functools import cache
from random import Random

import pytest
from conftest import REAL_PROFILE, assert_rate, number, raw, resolved

from emva_sim import leads, messages, phrases, profile
from emva_sim.leads import DatesGiven, Market

MESSAGE = "Tell us about your dream trip"


@pytest.fixture(scope="module")
def written(test_phrases):
    """A year of Leads at a setting, each with the message it writes."""

    @cache
    def at(setting="middle", seed=1):
        p = profile.resolve(raw(), setting)
        writer = messages.Writer(p, test_phrases)
        drawn = leads.draw_leads(Random(seed), p, date(2024, 1, 1), date(2024, 12, 31))
        rng = Random(seed + 100)
        return p, [(lead, writer.message(rng, lead)) for lead in drawn]

    return at


@pytest.fixture(scope="module")
def prose(written):
    """The Leads whose message is neither blank nor a token."""

    def at(setting="middle"):
        token = number(setting, "form.message.shape.token_words_at_most")
        return [(lead, text) for lead, text in written(setting)[1] if lead.message_words > token]

    return at


def test_every_message_has_exactly_the_leads_hidden_number_of_words(written):
    _, found = written()
    assert all(phrases.words(text.text) == lead.message_words for lead, text in found)
    assert {text.shape for lead, text in found if lead.message_words == 0} == {"blank"}


def test_the_same_seed_writes_the_same_messages_and_another_seed_others(written, test_phrases):
    p = resolved("middle")
    lead = written()[1][5][0]
    writer = messages.Writer(p, test_phrases)
    first = [writer.message(Random(7), lead).text for _ in range(2)]
    assert first[0] == first[1]
    others = {writer.message(Random(seed), lead).text for seed in range(8, 18)}
    assert len(others) > 1


def commitment_phrases(text):
    return [pid for pid in text.phrase_ids if ".commitment#" in pid]


def test_every_lead_with_a_decision_made_writes_one_and_no_other_lead_does(written):
    _, found = written()
    flagged = [text for lead, text in found if lead.text_commitment]
    assert flagged
    assert all(len(commitment_phrases(text)) == 1 for text in flagged)
    unflagged = [text for lead, text in found if not lead.text_commitment]
    assert not [text for text in unflagged if commitment_phrases(text)]
    # Only a Lead with no decision made writes that it is undecided.
    assert not [text for text in flagged if any(".undecided#" in pid for pid in text.phrase_ids)]


def test_vague_partly_and_very_specific_messages_follow_the_profiles_shares(written):
    shape = number("middle", "form.message.shape")
    found = Counter(text.shape for _, text in written()[1])
    n = sum(found.values())
    vague = number("middle", "form.message.vague_share")
    assert_rate(found["vague"], n, vague)
    specific = found["partly_specific"] + found["very_specific"]
    ratio = shape["partly_to_very_specific"]
    assert_rate(found["partly_specific"], specific, ratio / (1 + ratio))


def test_a_vague_message_gives_no_fact_but_a_rough_year(written):
    for _, text in written()[1]:
        if text.shape == "vague":
            groups = {pid.split("#")[0].split(".", 2)[2] for pid in text.phrase_ids}
            assert not groups & {"who", "when.exact", "when.month", "where.countries", "nights"}


def test_a_dreamer_names_every_country_it_chose_and_states_no_budget(written):
    p, found = written()
    dreamers = [(lead, text) for lead, text in found if text.shape == "dreamer"]
    assert dreamers
    names = p["text"]["languages"]
    for lead, text in dreamers:
        local = names[text.language]["countries"]
        assert all(local.get(c, c).lower() in text.text.lower() for c in lead.destinations)
        assert not any(".budget#" in pid for pid in text.phrase_ids)


@pytest.mark.parametrize("setting", ["middle", "form.message.written_in_french@high"])
def test_a_share_of_the_leads_from_france_write_in_french_and_no_one_else_does(written, setting):
    p, found = written(setting)
    french_from = p["text"]["french_from"]
    from_france = [text for lead, text in found if lead.country == french_from and text.text]
    french = [text for text in from_france if text.language == "fr"]
    assert_rate(len(french), len(from_france), number(setting, "form.message.written_in_french"))
    for lead, text in found:
        if text.language == "fr":
            assert lead.country == french_from and lead.market_group == Market.B
            assert all(pid.startswith("message.fr.") for pid in text.phrase_ids)


MENTIONS = [
    "ages_of_travellers",
    "named_birthday",
    "retirement",
    "religious_diet",
    "health_or_mobility",
    "pregnancy",
    "sexual_orientation",
    "names_of_travellers",
]


@pytest.mark.parametrize("mention", MENTIONS)
def test_each_prohibited_mention_is_planted_at_its_share_of_written_messages(prose, mention):
    found = prose()
    planted = [text for _, text in found if mention in text.mentions]
    assert_rate(len(planted), len(found), number("middle", f"form.message.mentions.{mention}"))
    for text in planted:
        assert any(f".prohibited.{mention}#" in pid for pid in text.phrase_ids)


def test_a_planted_mention_is_written_where_it_says(prose):
    # The ages and names are in the text, as the prohibited input would be.
    for lead, text in prose():
        if "names_of_travellers" in text.mentions and text.language == "en":
            first = lead.answers["First name"]
            pid = next(p for p in text.phrase_ids if ".names_of_travellers#" in p)
            if "{first_name}" in texts_of_bank()[pid]:
                assert first.lower() in text.text.lower()


@cache
def texts_of_bank():
    bank = phrases.load_bank(phrases.paths(REAL_PROFILE, raw())[0])
    return {p.id: p.text for p in phrases.bank_phrases(bank)}


@pytest.mark.parametrize("setting", ["middle", "form.message.facts_disagree_with_fields@high"])
def test_the_profiles_share_of_messages_state_a_fact_differently_from_the_form(written, setting):
    stating = [text for _, text in written(setting)[1] if text.fact_differs is not None]
    disagree = sum(bool(text.fact_differs) for text in stating)
    share = number(setting, "form.message.facts_disagree_with_fields")
    assert_rate(disagree, len(stating), share)


def test_a_message_that_disagrees_states_another_number_than_the_form(written):
    checked = 0
    for lead, text in written()[1]:
        if text.fact_differs == "nights" and text.language == "en":
            for phrase_id in text.phrase_ids:
                template = texts_of_bank()[phrase_id]
                if template == "Roughly {nights} nights.":
                    assert f"roughly {lead.nights} nights" not in text.text.lower()
                    assert re.search(r"roughly \d+ nights", text.text.lower())
                    checked += 1
    assert checked


def lead_with(lead, title="Mr", **fields):
    return replace(lead, answers={**lead.answers, "Title": title}, **fields)


def test_a_leads_facts_are_what_its_fields_say(written):
    lead = written()[1][0][0]
    solo = lead_with(
        lead, adults=1, children=0, dates_given=DatesGiven.YEAR, destinations=("Kenya",)
    )
    assert messages.facts(raw(), solo) >= {"solo", "undated", "to:Kenya", "male"}
    assert not messages.facts(raw(), solo) & {"partner", "couple", "two_or_more", "dated"}
    family = lead_with(lead, "Mrs", adults=2, children=2, dates_given=DatesGiven.EXACT)
    assert messages.facts(raw(), family) >= {"partner", "two_adults", "children", "dated", "female"}
    assert "couple" not in messages.facts(raw(), family)
    friends = lead_with(lead, "Dr", adults=4, children=0, repeat_client=True)
    assert messages.facts(raw(), friends) >= {"group", "partner", "repeat_client"}
    assert not messages.facts(raw(), friends) & {"male", "female", "couple", "first_time"}


@cache
def requirements():
    bank = phrases.load_bank(phrases.paths(REAL_PROFILE, raw())[0])
    return {p.id: p.requires for p in phrases.bank_phrases(bank)}


@pytest.mark.parametrize("setting", ["middle", "all-high"])
def test_no_message_says_what_the_leads_fields_contradict(written, setting):
    # Only the profile's share of messages state a fact unlike the form, by a changed number or
    # date (tested above); no phrase is ever written for a Lead its requirements do not fit.
    p, found = written(setting)
    broken = [
        (pid, sorted(requirements()[pid] - messages.facts(p, lead)), text.text)
        for lead, text in found
        for pid in text.phrase_ids
        if not requirements()[pid] <= messages.facts(p, lead)
    ]
    assert broken == []
    assert sum(bool(requirements()[pid]) for _, text in found for pid in text.phrase_ids) > 100
