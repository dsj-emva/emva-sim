"""Mess at intake, on simulated data: duplicates, bots or spam, and what the CRM holds wrongly.

One fixed seed, six months of leads. Each rate's tolerance is about three standard errors at its
own rate and size, written before the numbers were looked at.
"""

import csv
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2024, 7, 5))
EXPORT = "export/with-calls-and-notes"
DEALS = f"{EXPORT}/hubspot-crm-exports-safari-enquiries-2024-07-05.csv"
CONTACTS = f"{EXPORT}/hubspot-crm-exports-all-contacts-2024-07-05.csv"
TRUTH = "hidden-truth/hidden-truth.csv"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    made = {}

    def at(setting):
        if setting not in made:
            out = tmp_path_factory.mktemp("out")
            made[setting] = dataset.generate(PROFILE, setting, seed=1, out=out, history=HISTORY)
        return made[setting]

    return at


@pytest.fixture(scope="module")
def middle(generated):
    return generated("middle")


def kinds(folder, kind):
    return [r for r in rows(folder / TRUTH) if r["row_kind"] == kind]


@pytest.mark.parametrize(
    ("setting", "share", "tolerance"),
    [
        ("middle", 0.08, 0.016),
        ("mess.duplicate_leads@low", 0.02, 0.008),
        ("mess.duplicate_leads@high", 0.20, 0.021),
    ],
)
def test_the_profiles_share_of_rows_are_duplicate_leads(generated, setting, share, tolerance):
    folder = generated(setting)
    deals = rows(folder / DEALS)
    assert len(kinds(folder, "duplicate")) / len(deals) == pytest.approx(share, abs=tolerance)


def test_the_profiles_volume_counts_genuine_leads_only(middle):
    assert len(kinds(middle, "lead")) == 400 * 6
    assert len(rows(middle / DEALS)) == len(rows(middle / TRUTH))


def test_a_duplicate_is_the_same_person_again_later_as_a_second_contact(middle):
    contacts = {c["Associated Deal IDs"]: c for c in rows(middle / CONTACTS)}
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    genuine = {r["deal_record_id"]: r for r in kinds(middle, "lead")}
    duplicates = kinds(middle, "duplicate")
    assert duplicates
    for row in duplicates:
        original = row["duplicate_of_deal_record_id"]
        assert original in genuine
        again, first = contacts[row["deal_record_id"]], contacts[original]
        assert again["Record ID"] != first["Record ID"]
        assert again["Email"] != first["Email"]
        for name in ("First Name", "Last Name"):
            assert again[name].lower() == first[name].lower()
        assert deals[row["deal_record_id"]]["Create Date"] > deals[original]["Create Date"]
    assert any(contacts[r["deal_record_id"]]["First Name"].islower() for r in duplicates)


def test_duplicates_have_no_outcome_of_their_own_so_grading_can_leave_them_out(middle):
    for row in kinds(middle, "duplicate"):
        assert not row["win_propensity"] and not row["outcome"], row
    for row in kinds(middle, "lead"):
        assert row["win_propensity"] and row["outcome"] and not row["duplicate_of_deal_record_id"]


def test_the_exports_never_say_which_rows_are_duplicates_or_bots(middle):
    for path in sorted((middle / "export").rglob("*.csv")):
        header = " ".join(rows(path)[0]).lower()
        for word in ("duplicate", "bot", "spam", "row_kind", "kind"):
            assert word not in header, (path, word)
