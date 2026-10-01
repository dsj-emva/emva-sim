import math
import tomllib
from pathlib import Path

import pytest

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
CONFIDENCES = {"sourced", "estimated", "guessed"}
LADDER = {"Submitted", "Contact attempted", "Engaged", "Qualified", "Proposal", "Won", "Lost"}


def ranges(node, path=()):
    if isinstance(node, dict):
        if {"low", "middle", "high"} <= node.keys():
            yield ".".join(path), node
            return
        for key, value in node.items():
            yield from ranges(value, (*path, key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from ranges(value, (*path, str(i)))


@pytest.fixture(scope="module")
def profile():
    return tomllib.loads(PROFILE.read_text())


def test_every_range_is_ordered_with_a_confidence_and_a_source(profile):
    found = list(ranges(profile))
    assert found
    for name, r in found:
        assert r["low"] <= r["middle"] <= r["high"], name
        assert r["confidence"] in CONFIDENCES, name
        assert r["source"].strip(), name


def test_sourced_ranges_name_their_source(profile):
    for name, r in ranges(profile):
        if r["confidence"] == "sourced":
            assert r["source"] != "none", name


def test_the_pipeline_has_one_won_and_one_lost_stage_on_the_canonical_ladder(profile):
    stages = profile["pipeline"]["stages"]
    assert {s["ladder"] for s in stages} <= LADDER
    assert [s["closed"] for s in stages if "closed" in s] == ["won", "lost"]


def test_every_range_is_either_swept_or_held_at_its_middle(profile):
    swept = profile["sweep"]["one_at_a_time"]
    held = profile["sweep"]["held_at_middle"]
    assert sorted(swept + held) == sorted(name for name, _ in ranges(profile))


def test_the_sweep_gives_149_datasets(profile):
    assert 1 + 2 * len(profile["sweep"]["one_at_a_time"]) + 2 == 149


def test_every_effect_size_is_swept(profile):
    effects = [name for name, _ in ranges(profile) if name.startswith("effects.")]
    assert effects
    assert set(effects) <= set(profile["sweep"]["one_at_a_time"])


def test_every_effect_is_visible_from_a_canonical_stage(profile):
    for name, effect in profile["effects"].items():
        assert effect["visible"] in LADDER, name


def test_about_ten_in_a_hundred_enquiries_book_at_the_middle(profile):
    transitions = profile["process"]["transition"]
    contacted = 1 - profile["handling"]["neglected_share"]["middle"]
    won = contacted * math.prod(transitions[t]["middle"] for t in transitions)
    assert 0.09 <= won <= 0.12


def test_party_mix_leaves_a_share_for_solo_travellers(profile):
    middles = [r["middle"] for _, r in ranges(profile["form"]["party_mix"])]
    assert 0 < 1 - sum(middles) < 0.3


def test_listed_fields_are_on_the_form(profile):
    labels = {field["label"] for field in profile["form"]["fields"]}
    assert set(profile["prohibited_inputs"]["fields"]) <= labels
    assert set(profile["intent_signals"]["fields"]) <= labels


def test_national_origin_proxies_and_childrens_ages_are_prohibited(profile):
    prohibited = profile["prohibited_inputs"]
    assert {"Country of residence", "Ages of children"} <= set(prohibited["fields"])
    assert "the country code of Phone" in prohibited["parts_of_fields"]
    assert "the language the enquiry is written in" in prohibited["in_text"]


def test_pregnancy_and_sexual_orientation_are_planted_as_prohibited(profile):
    in_text = profile["prohibited_inputs"]["in_text"]
    assert "pregnancy" in in_text
    assert any(item.startswith("sexual orientation") for item in in_text)


def test_counts_of_adults_and_children_are_intent_signals(profile):
    assert {"Number of adults", "Number of children"} <= set(profile["intent_signals"]["fields"])


def test_loss_reason_meanings_match_their_ranges(profile):
    meanings = {r["meaning"] for r in profile["loss"]["reasons"]["recorded"]}
    shares = {key for key in profile["loss"]["reasons"] if key not in {"recorded", "source"}}
    assert meanings - {"unknown"} == shares
