"""The committed phrase bank and its cache of variations.

The bank must give the generator what it needs in every language; the cache, once the model has
written it (`make vary-phrases`), must hold a valid reply for every phrase. Until then the tests
that read the committed cache say so and skip; every other test reads the echoed test cache.
"""

import re
from functools import cache

import pytest
import separability
from conftest import REAL_PROFILE, raw
from test_text import (
    SEPARABILITY_SETTINGS,
    engaged_notes,
    separability_history,
    written_messages,
)

from emva_sim import dataset, form, messages, phrases

LANGUAGES = ["en", "fr"]
# Every fact a phrase may require (messages.facts).
FACTS = {
    "solo",
    "two_or_more",
    "partner",
    "couple",
    "two_adults",
    "children",
    "group",
    "dated",
    "undated",
    "budget",
    "no_budget",
    "repeat_client",
    "first_time",
    "committed",
    "uncommitted",
    "male",
    "female",
}
# Every slot the generator fills (messages.Writer.values, and bots' links).
SLOTS = {
    "adults",
    "children",
    "party",
    "nights",
    "date",
    "month",
    "year",
    "budget",
    "countries",
    "country",
    "park",
    "child_ages",
    "age",
    "age2",
    "companion",
    "first_name",
    "link",
}


@cache
def bank():
    return phrases.load_bank(phrases.paths(REAL_PROFILE, raw())[0])


def groups(prefix):
    found = {}
    for phrase in phrases.bank_phrases(bank()):
        if phrase.group.startswith(prefix):
            found.setdefault(phrase.group.removeprefix(prefix), []).append(phrase.text)
    return found


def test_every_requirement_a_phrase_names_is_a_fact_the_generator_knows():
    destinations = {o["label"] for o in form.field(raw(), "destinations")["options"]}
    known = FACTS | {f"to:{d}" for d in destinations}
    assert {r for p in phrases.bank_phrases(bank()) for r in p.requires} <= known


def test_every_slot_a_phrase_names_is_one_the_generator_fills():
    named = {slot for p in phrases.bank_phrases(bank()) for slot in phrases.slots(p.text)}
    assert named <= SLOTS


def test_each_language_has_every_group_a_message_is_written_from():
    english, french = groups("message.en."), groups("message.fr.")
    # Imperfect English is written only in English.
    assert set(english) - {"imperfect"} == set(french)
    mentions = {f"prohibited.{m}" for m in messages.MENTIONS}
    assert mentions <= set(english)


@pytest.mark.parametrize("language", LANGUAGES)
def test_a_decision_made_fits_the_shortest_written_message(language):
    # A written message has at least one word more than a token; a commitment phrase of two words
    # or fewer fits it, whatever the variations.
    shortest = raw()["form"]["message"]["shape"]["token_words_at_most"] + 1
    fit_anyone = [
        p
        for p in phrases.bank_phrases(bank())
        if p.group == f"message.{language}.commitment" and not p.requires
    ]
    assert min(phrases.words(p.text) for p in fit_anyone) <= 2 <= shortest


def test_every_recorded_loss_reason_has_its_free_text():
    recorded = {r["recorded"] for r in raw()["loss"]["reasons"]["recorded"]}
    assert set(groups("loss_reason.")) == recorded


def test_every_note_phrase_holds_an_expression_the_team_abbreviates_or_is_shorthand():
    abbreviations = raw()["text"]["abbreviations"]
    patterns = [rf"\b{re.escape(full)}\b" for full, _ in abbreviations]
    shorthand = [rf"(^|\s){re.escape(short)}(\s|$|[.,])" for _, short in abbreviations]
    shorthand += [r"\bx\d\b", r"\b\d(st|nd|rd|th)\b", r"\bthurs\b"]
    for group, texts in groups("notes.").items():
        if group.startswith("discovery."):
            continue  # always written after a recap
        for text in texts:
            found = [p for p in patterns + shorthand if re.search(p, text, re.IGNORECASE)]
            assert found, (group, text)


def test_every_lead_finds_a_twin_for_its_decision_in_the_shortest_written_message():
    # A Lead with a decision made writes a commitment phrase, every other Lead an undecided one;
    # each list has a phrase of two words or fewer that every Lead fits.
    for language in LANGUAGES:
        for group in ("commitment", "undecided"):
            short = [
                p
                for p in phrases.bank_phrases(bank())
                if p.group == f"message.{language}.{group}"
                and not p.requires
                and phrases.words(p.text) <= 2
            ]
            assert short, (language, group)


def committed():
    _, path = phrases.paths(REAL_PROFILE, raw())
    return phrases.read_cache(path, raw()["text"]["model"])


def missing():
    """The bank's phrases without a valid entry in the committed cache."""
    cached, text = committed()["phrases"], raw()["text"]
    unusable = []
    for phrase in phrases.bank_phrases(bank()):
        try:
            entry = cached.get(phrases.key(phrase.text))
            n = text["variations_per_phrase"]
            phrases.check_entry(bank(), phrase, entry, text["model"], n)
        except phrases.InvalidVariations:
            unusable.append(phrase.id)
    return unusable


def test_every_entry_in_the_committed_cache_is_valid_and_the_profiles_models():
    cached = committed()["phrases"]
    unusable = set(missing())
    in_cache = [p for p in phrases.bank_phrases(bank()) if phrases.key(p.text) in cached]
    assert not [p.id for p in in_cache if p.id in unusable]


def test_every_group_carrying_a_signal_says_what_it_carries():
    meanings = bank()["meaning"]
    for language in LANGUAGES:
        assert {f"message.{language}.commitment", f"message.{language}.undecided"} <= set(meanings)
    for side in ("real_buyer", "not_real_buyer"):
        assert f"notes.discovery.{side}" in meanings


needs_cache = pytest.mark.skipif(
    bool(missing()),
    reason=f"the committed cache lacks {len(missing())} phrases: run `make vary-phrases`",
)


@needs_cache
def test_the_committed_cache_covers_every_phrase_of_the_bank():
    assert missing() == []


@needs_cache
@pytest.mark.parametrize("setting", SEPARABILITY_SETTINGS)
def test_with_the_models_variations_no_short_phrase_tells_a_signal_apart(tmp_path, setting):
    history = separability_history(setting)
    folder = dataset.generate(REAL_PROFILE, setting, seed=1, out=tmp_path, history=history)
    found = written_messages(folder)
    commitment = [(text, row["text_commitment"] == "yes") for text, row, _ in found]
    for found in (commitment, engaged_notes(folder)):
        assert separability.separating(found) == [], separability.strongest(found)
