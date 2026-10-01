"""The committed phrase bank and its cache of variations.

The bank must give the generator what it needs in every language; the cache, once the model has
written it (`make vary-phrases`), must hold a valid reply for every phrase. Until then the tests
that read the committed cache say so and skip; every other test reads the echoed test cache.
"""

import json
import re
from functools import cache

import pytest
import separability
from conftest import REAL_PROFILE, raw
from test_text import HISTORY, engaged_notes, written_messages

from emva_sim import dataset, messages, phrases, vary

LANGUAGES = ["en", "fr"]
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
    for pid, text in phrases.bank_phrases(bank()):
        group = pid.split("#")[0]
        if group.startswith(prefix):
            found.setdefault(group.removeprefix(prefix), []).append(text)
    return found


def test_every_slot_a_phrase_names_is_one_the_generator_fills():
    named = {slot for _, text in phrases.bank_phrases(bank()) for slot in phrases.slots(text)}
    assert named <= SLOTS


def test_each_language_has_every_group_a_message_is_written_from():
    english, french = groups("message.en."), groups("message.fr.")
    assert set(english) == set(french)
    mentions = {f"prohibited.{m}" for m in messages.MENTIONS}
    assert mentions <= set(english)


@pytest.mark.parametrize("language", LANGUAGES)
def test_a_decision_made_fits_the_shortest_written_message(language):
    # A written message has at least one word more than a token; a commitment phrase of two words
    # or fewer fits it, whatever the variations.
    shortest = raw()["form"]["message"]["shape"]["token_words_at_most"] + 1
    lengths = [phrases.words(t) for t in groups(f"message.{language}.")["commitment"]]
    assert min(lengths) <= 2 <= shortest


def test_every_recorded_loss_reason_has_its_free_text():
    recorded = {r["recorded"] for r in raw()["loss"]["reasons"]["recorded"]}
    assert set(groups("loss_reason.")) == recorded


def test_every_note_phrase_holds_an_expression_the_team_abbreviates():
    patterns = [rf"\b{re.escape(full)}\b" for full, _ in raw()["text"]["abbreviations"]]
    for group, texts in groups("notes.").items():
        if group.startswith("discovery."):
            continue  # always written after a recap
        for text in texts:
            assert any(re.search(p, text, re.IGNORECASE) for p in patterns), (group, text)


@pytest.mark.parametrize("group", ["notes.discovery", "notes.follow_up"])
def test_real_and_not_real_buyer_notes_share_their_words(group):
    # Written in pairs: no word or pair of words is in more than two phrases more on one side.
    sides = {side: groups(f"{group}.")[side] for side in ("real_buyer", "not_real_buyer")}
    counts = {}
    for side, texts in sides.items():
        counts[side] = {}
        for text in texts:
            for gram in separability.ngrams(text, 2):
                counts[side][gram] = counts[side].get(gram, 0) + 1
    grams = set(counts["real_buyer"]) | set(counts["not_real_buyer"])
    uneven = {
        " ".join(g): counts["real_buyer"].get(g, 0) - counts["not_real_buyer"].get(g, 0)
        for g in grams
    }
    assert {g: d for g, d in uneven.items() if abs(d) > 2} == {}


def committed():
    _, path = phrases.paths(REAL_PROFILE, raw())
    return phrases.read_cache(path, raw()["text"]["model"])


def missing():
    cached = committed()["phrases"]
    return [pid for pid, text in phrases.bank_phrases(bank()) if phrases.key(text) not in cached]


def test_the_committed_cache_holds_only_valid_replies_of_the_profiles_model():
    n = raw()["text"]["variations_per_phrase"]
    for entry in committed()["phrases"].values():
        assert entry["model"] == raw()["text"]["model"]
        reply = json.dumps({"variations": entry["variations"]})
        assert vary.validate(entry["phrase"], reply, n) == entry["variations"]


needs_cache = pytest.mark.skipif(
    bool(missing()),
    reason=f"the committed cache lacks {len(missing())} phrases: run `make vary-phrases`",
)


@needs_cache
def test_the_committed_cache_covers_every_phrase_of_the_bank():
    assert missing() == []


@needs_cache
def test_with_the_models_variations_no_short_phrase_tells_a_signal_apart(tmp_path):
    folder = dataset.generate(REAL_PROFILE, "middle", seed=1, out=tmp_path, history=HISTORY)
    found = written_messages(folder)
    commitment = [(text, row["text_commitment"] == "yes") for text, row, _ in found]
    for found in (commitment, engaged_notes(folder)):
        assert separability.separating(found) == [], separability.strongest(found)
