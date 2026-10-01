import re
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
    assert len(with_children) / len(drawn) == pytest.approx(0.28, abs=0.03)


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
    assert share(answers(drawn, label), answer) == pytest.approx(expected, abs=0.03)


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
