"""The phrase bank and the cache of its variations: generation reads only the cache."""

import pytest

from emva_sim import phrases
from emva_sim.phrases import MissingVariations, Phrases

BANK = {
    "about": {"message": "an enquiry"},
    "message": {"en": {"token": ["Call me", "See above"]}},
}


def cache_of(*texts):
    return {
        "model": "test",
        "phrases": {
            phrases.key(t): {"phrase": t, "variations": [f"{t}!"], "model": "test"} for t in texts
        },
    }


def test_each_phrase_is_offered_with_its_cached_variations():
    found = Phrases(BANK, cache_of("Call me", "See above")).group("message.en.token")
    assert [p.id for p in found] == ["message.en.token#1", "message.en.token#2"]
    assert found[0].options == ("Call me", "Call me!")


def test_a_phrase_with_no_cached_variations_stops_generation_and_names_the_command():
    with pytest.raises(MissingVariations, match="make vary-phrases") as error:
        Phrases(BANK, cache_of("Call me"))
    assert "message.en.token#2" in str(error.value)


def test_the_about_table_describes_the_text_and_holds_no_phrases():
    assert [pid for pid, _ in phrases.bank_phrases(BANK)] == [
        "message.en.token#1",
        "message.en.token#2",
    ]


def test_the_cache_is_written_in_a_stable_order(tmp_path):
    path = tmp_path / "cache.json"
    first = cache_of("See above", "Call me")
    phrases.write_cache(path, first)
    written = path.read_text()
    phrases.write_cache(path, phrases.read_cache(path, "test"))
    assert path.read_text() == written
    keys = sorted(first["phrases"])
    assert written.index(keys[0]) < written.index(keys[1])
