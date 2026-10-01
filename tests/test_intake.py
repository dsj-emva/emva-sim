"""Mess at intake, on simulated data: duplicates, bots or spam, and what the CRM holds wrongly.

One fixed seed, six months of leads. Each rate is checked at the middle and at its range's low and
high ends, within three standard errors at the size measured.
"""

import re
from datetime import date

import pytest
from conftest import PROFILE, TRUTH, assert_rate, ends, kinds, number, raw, resolved, rows

from emva_sim import dataset, form, leads
from emva_sim.hidden_truth import TRUE_PATH_COLUMNS
from emva_sim.intake import RowKind
from emva_sim.people import FIRST_NAMES

HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2024, 7, 5))
MONTHS = 6
EXPORT = "export/with-calls-and-notes"
DEALS = f"{EXPORT}/hubspot-crm-exports-safari-enquiries-2024-07-05.csv"
CONTACTS = f"{EXPORT}/hubspot-crm-exports-all-contacts-2024-07-05.csv"
KEY_FIELDS = [form.field(raw(), role)["label"] for role in raw()["mess"]["key_fields"]]


def column(label):
    """The contacts export's column for a form field."""
    return raw()["exports"]["contact_properties"].get(label, label)


@pytest.fixture(scope="module")
def generated(generate):
    return lambda setting: generate(setting, HISTORY)


@pytest.fixture(scope="module")
def middle(generated):
    return generated("middle")


def contact_of_deal(folder):
    """Each deal's contact row, by deal Record ID."""
    return {
        deal: contact
        for contact in rows(folder / CONTACTS)
        for deal in contact["Associated Deal IDs"].split(";")
    }


def with_contacts(folder, kind):
    contacts = contact_of_deal(folder)
    return [(contacts[r["deal_record_id"]], r) for r in kinds(folder, kind)]


def altered(row):
    named = row["fields_missing_or_wrong"]
    return named.split(";") if named else []


@pytest.mark.parametrize("setting", ends("mess.duplicate_leads"))
def test_the_profiles_share_of_rows_are_duplicate_leads(generated, setting):
    folder = generated(setting)
    duplicates = len(kinds(folder, RowKind.DUPLICATE))
    assert_rate(duplicates, len(rows(folder / DEALS)), number(setting, "mess.duplicate_leads"))


def test_the_profiles_volume_counts_genuine_leads_only(middle):
    volume = number("middle", "volume.leads_per_month")
    assert len(kinds(middle, RowKind.LEAD)) == volume * MONTHS
    assert len(rows(middle / DEALS)) == len(rows(middle / TRUTH))


def test_a_duplicate_is_the_same_person_again_later_as_a_second_contact(middle):
    contacts = contact_of_deal(middle)
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    genuine = {r["deal_record_id"]: r for r in kinds(middle, RowKind.LEAD)}
    duplicates = kinds(middle, RowKind.DUPLICATE)
    assert duplicates
    for row in duplicates:
        original = row["duplicate_of_deal_record_id"]
        assert original in genuine
        again, first = contacts[row["deal_record_id"]], contacts[original]
        assert again["Record ID"] != first["Record ID"]
        assert again["Email"] != first["Email"]
        for label in ("First name", "Last name"):
            if label not in altered(genuine[original]):
                assert again[column(label)].lower() == first[column(label)].lower()
        assert deals[row["deal_record_id"]]["Create Date"] >= deals[original]["Create Date"]
    assert any(contacts[r["deal_record_id"]]["First Name"].islower() for r in duplicates)


def test_duplicates_have_no_outcome_of_their_own_so_grading_can_leave_them_out(middle):
    for row in kinds(middle, RowKind.DUPLICATE):
        assert not row["win_propensity"] and not row["outcome"], row
    for row in kinds(middle, RowKind.LEAD):
        assert row["win_propensity"] and row["outcome"] and not row["duplicate_of_deal_record_id"]


@pytest.mark.parametrize("setting", ends("mess.bot_or_spam"))
def test_the_profiles_share_of_rows_are_bot_or_spam(generated, setting):
    folder = generated(setting)
    bots = len(kinds(folder, RowKind.BOT))
    assert_rate(bots, len(rows(folder / DEALS)), number(setting, "mess.bot_or_spam"))


def junk_signs(contact):
    """The patterns of a bot or spam submission this contact shows."""
    adults = float(contact["Number of adults"] or 1)
    children = float(contact["Number of children"] or 0)
    signs = {
        "made-up name": contact["First Name"].capitalize() not in sum(FIRST_NAMES.values(), []),
        "disposable email": contact["Email"].endswith(".example"),
        "links in the message": "http" in contact["Message"],
        "empty message": not contact["Message"],
        "impossible party": adults == 0 or adults > 20 or children > 12,
    }
    return {sign for sign, shown in signs.items() if shown}


def test_bots_look_like_junk_and_genuine_leads_held_rightly_do_not(middle):
    bots = with_contacts(middle, RowKind.BOT)
    assert bots
    seen = set()
    for bot, _ in bots:
        signs = junk_signs(bot)
        assert signs - {"empty message"}, bot
        seen |= signs
    assert seen == {
        "made-up name",
        "disposable email",
        "links in the message",
        "empty message",
        "impossible party",
    }
    for contact, row in with_contacts(middle, RowKind.LEAD) + with_contacts(
        middle, RowKind.DUPLICATE
    ):
        if not altered(row):
            assert not junk_signs(contact) - {"empty message"}


def test_bots_have_no_outcome_so_grading_can_leave_them_out(middle):
    for row in kinds(middle, RowKind.BOT):
        assert not row["win_propensity"] and not row["outcome"], row
        assert not row["duplicate_of_deal_record_id"]


VALID_EMAIL = re.compile(r"[A-Za-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+")


def valid_phone():
    formats = [f for c in leads.countries(raw()) for f in c["phones"]]
    patterns = [re.escape(f).replace("\\#", "#").replace("#", r"\d") for f in formats]
    return re.compile("|".join(f"(?:{p})" for p in patterns))


@pytest.mark.parametrize("setting", ends("mess.invalid_email"))
def test_the_profiles_share_of_genuine_leads_have_an_invalid_email(generated, setting):
    contacts = with_contacts(generated(setting), RowKind.LEAD)
    invalid = [(c, r) for c, r in contacts if not VALID_EMAIL.fullmatch(c["Email"])]
    assert_rate(len(invalid), len(contacts), number(setting, "mess.invalid_email"))
    assert all(r["invalid_email"] == "yes" for _, r in invalid)
    assert sum(r["invalid_email"] == "yes" for _, r in contacts) == len(invalid)


@pytest.mark.parametrize("setting", ends("mess.invalid_phone"))
def test_the_profiles_share_of_given_phones_are_invalid(generated, setting):
    valid = valid_phone()
    given = [
        (c, r) for c, r in with_contacts(generated(setting), RowKind.LEAD) if c["Phone Number"]
    ]
    invalid = [(c, r) for c, r in given if not valid.fullmatch(c["Phone Number"])]
    assert_rate(len(invalid), len(given), number(setting, "mess.invalid_phone"))
    assert all(r["invalid_phone"] == "yes" for _, r in invalid)
    assert sum(r["invalid_phone"] == "yes" for _, r in given) == len(invalid)


@pytest.mark.parametrize("setting", ends("mess.field_missing_or_wrong"))
def test_the_profiles_share_of_genuine_records_have_a_key_field_missing_or_wrong(
    generated, setting
):
    contacts = with_contacts(generated(setting), RowKind.LEAD)
    messy = [r for _, r in contacts if altered(r)]
    assert_rate(len(messy), len(contacts), number(setting, "mess.field_missing_or_wrong"))
    assert {field for r in messy for field in altered(r)} == set(KEY_FIELDS)


def test_a_required_key_field_is_blank_only_where_the_hidden_truth_says_it_is_missing(middle):
    required = [f["label"] for f in resolved("middle")["form"]["fields"] if f["required"]]
    blank = wrong = 0
    for contact, row in with_contacts(middle, RowKind.LEAD):
        for field in altered(row):
            if contact[column(field)]:
                wrong += 1
            else:
                blank += 1
        for field in set(required) & set(KEY_FIELDS):
            if not contact[column(field)]:
                assert field in altered(row), (field, row)
    assert blank and wrong


@pytest.mark.parametrize(
    "setting",
    ["mess.bot_or_spam@high", "mess.duplicate_leads@high", "recording.lag_days_median@high"],
)
def test_the_mess_never_changes_a_leads_true_path(generated, middle, setting):
    def true_paths(folder):
        return [[r[c] for c in TRUE_PATH_COLUMNS] for r in kinds(folder, RowKind.LEAD)]

    assert true_paths(generated(setting)) == true_paths(middle)


def files(folder):
    return {p.relative_to(folder): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def test_the_same_seed_gives_the_same_mess(tmp_path):
    month = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 31), export=date(2024, 3, 1))
    first = dataset.generate(PROFILE, "all-high", seed=5, out=tmp_path / "a", history=month)
    second = dataset.generate(PROFILE, "all-high", seed=5, out=tmp_path / "b", history=month)
    assert files(first) == files(second)
    truth = rows(first / TRUTH)
    assert {r["row_kind"] for r in truth} == set(RowKind)
    assert any(r["fields_missing_or_wrong"] for r in truth)


def test_the_exports_never_say_which_rows_are_duplicates_or_bots(middle):
    for path in sorted((middle / "export").rglob("*.csv")):
        header = " ".join(rows(path)[0]).lower()
        for word in ("duplicate", "bot", "spam", "row_kind", "kind"):
            assert word not in header, (path, word)
