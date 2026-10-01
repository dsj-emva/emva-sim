import tomllib
from pathlib import Path

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
CONFIDENCES = {"sourced", "estimated", "guessed"}


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


def load():
    return tomllib.loads(PROFILE.read_text())


def test_every_range_is_ordered_with_a_confidence_and_a_source():
    found = list(ranges(load()))
    assert found
    for name, r in found:
        assert r["low"] <= r["middle"] <= r["high"], name
        assert r["confidence"] in CONFIDENCES, name
        assert r["source"].strip(), name


def test_sourced_ranges_name_their_source():
    for name, r in ranges(load()):
        if r["confidence"] == "sourced":
            assert r["source"] != "none", name


def test_the_pipeline_has_one_won_and_one_lost_stage_on_the_canonical_ladder():
    ladder = {"Submitted", "Contact attempted", "Engaged", "Qualified", "Proposal", "Won", "Lost"}
    stages = load()["pipeline"]["stages"]
    assert {s["ladder"] for s in stages} <= ladder
    assert [s["closed"] for s in stages if "closed" in s] == ["won", "lost"]


def test_every_range_is_either_swept_or_held_at_its_middle():
    profile = load()
    swept = profile["sweep"]["one_at_a_time"]
    held = profile["sweep"]["held_at_middle"]
    names = [name for name, _ in ranges(profile)]
    assert sorted(swept + held) == sorted(names)


def test_every_effect_size_is_swept():
    swept = load()["sweep"]["one_at_a_time"]
    effects = [name for name, _ in ranges(load()) if name.startswith("effects.")]
    assert effects
    assert set(effects) <= set(swept)


def test_national_origin_proxies_are_prohibited_and_children_counts_are_intent_signals():
    profile = load()
    prohibited = profile["prohibited_inputs"]
    assert {"Country of residence", "Phone (country code)", "Ages of children"} <= set(
        prohibited["fields"]
    )
    assert {"the language the enquiry is written in", "pregnancy"} <= set(prohibited["in_text"])
    assert {"Number of adults", "Number of children"} <= set(profile["intent_signals"]["fields"])
