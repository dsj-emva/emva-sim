from pathlib import Path

import pytest

from emva_sim import profile

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"


@pytest.fixture(scope="module")
def raw():
    return profile.load(PROFILE)


def test_middle_puts_every_range_at_its_middle(raw):
    resolved = profile.resolve(raw, "middle")
    assert resolved["volume"]["leads_per_month"] == 400
    assert resolved["process"]["transition"]["won"] == 0.25
    assert resolved["effects"]["budget_floor"]["below_half"] == 0.10


def test_plain_values_are_kept(raw):
    resolved = profile.resolve(raw, "middle")
    assert resolved["pipeline"]["name"] == "Safari Enquiries"
    assert resolved["effects"]["lead_time_by_season"]["peak_months"] == [7, 8, 9, 10]


def test_one_range_at_its_low_keeps_every_other_range_at_its_middle(raw):
    resolved = profile.resolve(raw, "volume.leads_per_month@low")
    assert resolved["volume"]["leads_per_month"] == 100
    assert resolved["process"]["transition"]["won"] == 0.25


def test_one_range_at_its_high(raw):
    resolved = profile.resolve(raw, "effects.lead_source.referral@high")
    assert resolved["effects"]["lead_source"]["referral"] == 6.0
    assert resolved["effects"]["lead_source"]["organic"] == 1.4


def test_all_low_and_all_high(raw):
    low = profile.resolve(raw, "all-low")
    high = profile.resolve(raw, "all-high")
    assert low["volume"]["leads_per_month"] == 100
    assert low["handling"]["neglected_share"] == 0.0
    assert high["volume"]["leads_per_month"] == 1000
    assert high["deal"]["price_per_person_per_night"]["ultra_luxury"] == 5000


def test_every_swept_name_is_a_range_name(raw):
    names = set(profile.range_names(raw))
    assert set(raw["sweep"]["one_at_a_time"]) <= names
    assert "volume.leads_per_month" in names


@pytest.mark.parametrize(
    "setting",
    ["mid", "volume.leads_per_month", "volume.leads_per_month@middle", "volume@low", "nope@high"],
)
def test_an_unknown_setting_is_rejected(raw, setting):
    with pytest.raises(profile.UnknownSetting):
        profile.resolve(raw, setting)
