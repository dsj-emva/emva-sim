from datetime import date
from pathlib import Path
from random import Random

import pytest

from emva_sim import leads, profile

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
PEAK = (7, 8, 9, 10)


@pytest.fixture(scope="module")
def drawn():
    p = profile.resolve(profile.load(PROFILE), "middle")
    return leads.draw_leads(Random(1), p, date(2024, 1, 1), date(2024, 3, 31))


def test_the_profiles_price_is_the_season_average(drawn):
    # Luxury averages $1,300 a night; peak (4 of 12 travel months) pays 1.4 times low season:
    # low = 1300 / (8/12 + 4/12 x 1.4) = 1147.06, peak = 1.4 x low = 1605.88.
    luxury = [lead for lead in drawn if lead.style == "luxury"]
    peak = [lead.price_per_person_per_night for lead in luxury if lead.travel_at.month in PEAK]
    low = [lead.price_per_person_per_night for lead in luxury if lead.travel_at.month not in PEAK]
    assert peak and low
    assert peak == pytest.approx([1605.88] * len(peak), abs=0.01)
    assert low == pytest.approx([1147.06] * len(low), abs=0.01)


def test_the_base_draws_read_no_planted_effect():
    p = profile.resolve(profile.load(PROFILE), "middle")
    del p["effects"]
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
    assert all(lead.adults == 2 for lead in with_children)
    assert len(with_children) / len(drawn) == pytest.approx(0.28, abs=0.03)
