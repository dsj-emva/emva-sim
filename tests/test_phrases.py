"""The phrase bank and the cache of its variations: generation reads only the cache, and only
entries that pass every rule."""

import pytest

from emva_sim import phrases
from emva_sim.phrases import InvalidVariations, MissingVariations, Phrases

BANK = {
    "about": {"message": "an enquiry"},
    "meaning": {"message.en.commitment": "the trip is decided"},
    "message": {
        "en": {
            "token": ["Call me", {"text": "Call us both", "requires": ["not_solo"]}],
            "commitment": ["Flights booked."],
        }
    },
}
N = 2


def entry(text, variations, model="test", answers=None):
    found = {"phrase": text, "variations": variations, "model": model}
    if answers is not None:
        found["meaning_check"] = {"statement": "the trip is decided", "answers": answers}
    return found


def cache_of(**entries):
    return {"model": "test", "phrases": {phrases.key(t): e for t, e in entries.items()}}


def good():
    return {
        "Call me": entry("Call me", ["Call me!", "call me"]),
        "Call us both": entry("Call us both", ["Call us both!", "call us both"]),
        "Flights booked.": entry(
            "Flights booked.", ["Flights booked!", "flights booked."], answers=["yes", "yes"]
        ),
    }


def test_each_phrase_is_offered_with_its_cached_variations_and_its_requirements():
    found = Phrases(BANK, cache_of(**good()), "test", N).group("message.en.token")
    assert [p.id for p in found] == ["message.en.token#1", "message.en.token#2"]
    assert found[0].options == ("Call me", "Call me!", "call me")
    assert found[1].requires == {"not_solo"}


def test_a_phrase_with_no_cached_variations_stops_generation_and_names_the_command():
    entries = good()
    del entries["Call us both"]
    with pytest.raises(MissingVariations, match="make vary-phrases") as error:
        Phrases(BANK, cache_of(**entries), "test", N)
    assert "message.en.token#2" in str(error.value)


def test_an_entry_another_model_wrote_stops_generation():
    entries = good()
    entries["Call me"] = entry("Call me", ["Call me!", "call me"], model="other")
    with pytest.raises(MissingVariations, match="'other'"):
        Phrases(BANK, cache_of(**entries), "test", N)


def test_every_cached_entry_is_checked_again_when_the_cache_is_loaded():
    entries = good()
    entries["Call me"] = entry("Call me", ["Call me!", "Call Tom"])
    with pytest.raises(MissingVariations, match="capitalised"):
        Phrases(BANK, cache_of(**entries), "test", N)


@pytest.mark.parametrize(
    "answers", [None, ["yes", "no"], ["yes"]], ids=["unchecked", "drifted", "half-checked"]
)
def test_a_signal_phrase_needs_every_variation_checked_to_say_what_it_says(answers):
    entries = good()
    entries["Flights booked."] = entry(
        "Flights booked.", ["Flights booked!", "flights booked."], answers=answers
    )
    with pytest.raises(MissingVariations, match="checked to say"):
        Phrases(BANK, cache_of(**entries), "test", N)


def test_the_about_and_meaning_tables_hold_no_phrases():
    assert [p.id for p in phrases.bank_phrases(BANK)] == [
        "message.en.token#1",
        "message.en.token#2",
        "message.en.commitment#1",
    ]


@pytest.mark.parametrize(
    ("phrase", "variation", "reason"),
    [
        ("Some time in {month}.", "Around {month}, 2025.", "number"),
        ("We'd love to visit {countries}.", "Visiting {countries} and Zanzibar.", "capital"),
        ("Call me", "Call me now", "one line"),
        ("Call me", "Call me\rnow", "one line"),
        ("Call me", "Call me\x85now", "one line"),
        ("Some time in {month}.", "Some time in {months}.", "slots"),
        ("Some time in {month}.", "Some time in {month} {month}.", "slots"),
        ("Some time in {month}.", "Some time in {month}}.", "slots"),
        ("Some time in {month}.", "Some time in {month} or {", "slots"),
    ],
)
def test_a_variation_that_adds_a_fact_or_breaks_the_form_is_refused(phrase, variation, reason):
    with pytest.raises(InvalidVariations, match=reason):
        phrases.check(phrase, [variation], 1)


@pytest.mark.parametrize(
    ("phrase", "variation"),
    [
        ("We arrive on {date}.", "Arriving {date}. Can't wait!"),
        ("Gorillas are a must.", "I really want the gorillas."),
        ("We'd love to see the Big Five.", "Seeing the Big Five would be lovely."),
        ("Some time in {year}.", "In {year}, I think."),
    ],
    ids=["a new sentence", "I", "a capitalised word of", "the year slot"],
)
def test_a_variation_may_start_sentences_say_i_and_keep_the_phrases_names(phrase, variation):
    assert phrases.check(phrase, [variation], 1) == [variation]


def test_the_cache_is_written_in_a_stable_order(tmp_path):
    path = tmp_path / "cache.json"
    first = cache_of(**good())
    phrases.write_cache(path, first)
    written = path.read_text()
    phrases.write_cache(path, phrases.read_cache(path, "test"))
    assert path.read_text() == written
    keys = sorted(first["phrases"])
    assert written.index(keys[0]) < written.index(keys[1])
