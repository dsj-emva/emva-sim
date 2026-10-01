import csv
import io
import re
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset, profile
from emva_sim.process import Process

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2024, 7, 5))
DEALS = "export/with-calls-and-notes/hubspot-crm-exports-safari-enquiries-2024-07-05.csv"
CONTACTS = "export/with-calls-and-notes/hubspot-crm-exports-all-contacts-2024-07-05.csv"
CALLS = "export/with-calls-and-notes/hubspot-crm-exports-all-calls-2024-07-05.csv"
TRUTH = "hidden-truth/hidden-truth.csv"
STAGE_HISTORY = "hidden-truth/stage-history.csv"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def raw():
    return profile.load(PROFILE)


@pytest.fixture(scope="module")
def middle(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    return dataset.generate(PROFILE, "middle", seed=1, out=out, history=HISTORY)


def genuine(truth_rows):
    """The hidden truth's rows of genuine Leads, without duplicates and bots."""
    return [r for r in truth_rows if r["row_kind"] == "lead"]


def test_the_deals_export_has_one_deal_per_lead_at_the_profiles_volume(middle):
    deals = rows(middle / DEALS)
    assert len(genuine(rows(middle / TRUTH))) == 400 * 6
    assert len(deals) == len(rows(middle / TRUTH))
    assert list(deals[0])[0] == "Record ID"


SHORT = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 31), export=date(2024, 3, 1))


def files(folder):
    return {p.relative_to(folder): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def test_the_same_seed_gives_byte_identical_files(tmp_path):
    first = dataset.generate(PROFILE, "middle", seed=7, out=tmp_path / "a", history=SHORT)
    second = dataset.generate(PROFILE, "middle", seed=7, out=tmp_path / "b", history=SHORT)
    assert files(first) == files(second)
    assert len(files(first)) == 7


def sweep_settings(raw):
    one_at_a_time = raw["sweep"]["one_at_a_time"]
    ends = [f"{name}@{end}" for name in one_at_a_time for end in ("low", "high")]
    return ["middle", *ends, "all-low", "all-high"]


def test_every_dataset_of_the_sweep_generates(raw, tmp_path):
    tiny = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 2), export=date(2024, 3, 1))
    settings = sweep_settings(raw)
    assert len(settings) == 149
    for setting in settings:
        folder = dataset.generate(PROFILE, setting, seed=1, out=tmp_path, history=tiny)
        assert rows(folder / TRUTH), setting


def test_the_hidden_truth_gives_a_deal_value_only_to_quoted_or_won_deals(middle):
    truth = rows(middle / TRUTH)
    for row in truth:
        quoted = row["reached_stage"] in {"Proposal", "Won"}
        assert bool(row["deal_value"]) == quoted, row
    assert any(row["deal_value"] for row in truth)


def test_a_lead_won_after_the_export_date_is_not_closed_won_in_the_export(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    won_later = [r for r in rows(middle / TRUTH) if r["won_at"] >= "2024-07-05"]
    assert won_later
    for row in won_later:
        deal = deals[row["deal_record_id"]]
        assert deal["Deal Stage"] != "Deposit Paid"
        assert deal['Date entered "Deposit Paid (Safari Enquiries)"'] == ""


LONG_AFTER = dataset.History(
    start=date(2024, 1, 1), end=date(2024, 3, 31), export=date(2025, 12, 31)
)
LONG_CALLS = "export/with-calls-and-notes/hubspot-crm-exports-all-calls-2025-12-31.csv"


def logged_share(tmp_path, setting):
    folder = dataset.generate(PROFILE, setting, seed=1, out=tmp_path, history=LONG_AFTER)
    made = sum(int(r["call_attempts"]) for r in genuine(rows(folder / TRUTH)))
    return len(rows(folder / LONG_CALLS)) / made


@pytest.mark.parametrize(
    ("setting", "share"),
    [
        ("middle", 0.50),
        ("handling.attempts_logged@low", 0.25),
        ("handling.attempts_logged@high", 0.80),
    ],
)
def test_the_calls_export_logs_the_profiles_share_of_call_attempts(tmp_path, setting, share):
    assert logged_share(tmp_path, setting) == pytest.approx(share, abs=0.06)


def test_a_partial_month_gets_its_share_of_the_months_volume(tmp_path):
    two_days = dataset.History(
        start=date(2024, 1, 1), end=date(2024, 1, 2), export=date(2024, 3, 1)
    )
    folder = dataset.generate(PROFILE, "middle", seed=1, out=tmp_path, history=two_days)
    assert len(genuine(rows(folder / TRUTH))) == round(400 * 2 / 31)


def test_a_median_delay_that_contradicts_the_late_share_is_refused():
    p = profile.resolve(profile.load(PROFILE), "middle")
    p["handling"]["first_attempt_delay_median_hours"] = 24
    with pytest.raises(ValueError, match="a median of 24"):
        Process(p)


def test_generating_again_replaces_the_previous_dataset(tmp_path):
    dataset.generate(PROFILE, "middle", seed=7, out=tmp_path, history=SHORT)
    later = dataset.History(start=SHORT.start, end=SHORT.end, export=date(2024, 4, 1))
    folder = dataset.generate(PROFILE, "middle", seed=7, out=tmp_path, history=later)
    assert len(files(folder)) == 7
    assert all("2024-04-01" in str(p) for p in files(folder) if "export" in str(p))


def test_a_different_seed_gives_different_files(tmp_path):
    first = dataset.generate(PROFILE, "middle", seed=7, out=tmp_path, history=SHORT)
    second = dataset.generate(PROFILE, "middle", seed=8, out=tmp_path, history=SHORT)
    assert first != second
    assert all(a != b for a, b in zip(files(first).values(), files(second).values(), strict=True))


def test_the_dataset_folder_holds_both_export_variants_and_the_hidden_truth(middle):
    names = {str(p) for p in files(middle)}
    assert names == {
        DEALS,
        CONTACTS,
        CALLS,
        DEALS.replace("with-calls-and-notes", "deals-and-contacts-only"),
        CONTACTS.replace("with-calls-and-notes", "deals-and-contacts-only"),
        TRUTH,
        STAGE_HISTORY,
    }
    assert middle.name == "planned-hospitality-middle-seed-1"


def export_files(folder):
    return sorted((folder / "export").rglob("*.csv"))


def test_no_hidden_truth_column_appears_in_any_export(middle):
    truth_columns = set(rows(middle / TRUTH)[0])
    for path in export_files(middle):
        header = set(rows(path)[0])
        assert not header & truth_columns, path
        assert not {h for h in header if "propensity" in h.lower() or "truth" in h.lower()}


def test_every_field_is_double_quoted(middle):
    for path in [*export_files(middle), middle / TRUTH, middle / STAGE_HISTORY]:
        with open(path, newline="", encoding="utf-8") as f:
            raw = list(csv.reader(f))
        quoted = io.StringIO(newline="")
        csv.writer(quoted, quoting=csv.QUOTE_ALL).writerows(raw)
        assert path.read_bytes().decode("utf-8") == quoted.getvalue(), path


DATETIME = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


def test_datetimes_are_minutes_with_no_zone_and_all_before_the_export_date(middle):
    for path in export_files(middle):
        for row in rows(path):
            for column, value in row.items():
                if value and ("Date" in column or column == "Activity date"):
                    assert DATETIME.fullmatch(value), (column, value)
                    assert value < "2024-07-05", (column, value)


def test_deals_carry_the_pipeline_and_its_crm_stages(middle, raw):
    stages = [s["name"] for s in raw["pipeline"]["stages"]]
    deals = rows(middle / DEALS)
    header = list(deals[0])
    assert header[:12] == [
        "Record ID",
        "Deal Name",
        "Pipeline",
        "Deal Stage",
        "Amount",
        "Close Date",
        "Create Date",
        "Deal owner",
        "Deal Type",
        "Closed Lost Reason",
        "Original Traffic Source",
        "Record source",
    ]
    for stage in stages:
        assert f'Date entered "{stage} (Safari Enquiries)"' in header
    assert set(raw["exports"]["deal_properties"]) <= set(header)
    assert header[-2:] == ["Associated Contact", "Associated Contact IDs"]
    assert {d["Pipeline"] for d in deals} == {"Safari Enquiries"}
    assert {d["Deal Stage"] for d in deals} <= set(stages)
    assert {"New Enquiry", "Attempting Contact", "Deposit Paid", "Lost"} <= {
        d["Deal Stage"] for d in deals
    }
    assert {d["Original Traffic Source"] for d in deals} == {
        "Paid Search",
        "Organic Search",
        "Paid Social",
        "Referrals",
    }
    assert set(raw["team"]["owners"]) == {d["Deal owner"] for d in deals}


def test_contacts_use_hubspot_labels_and_point_at_their_deals(middle):
    contacts = rows(middle / CONTACTS)
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    header = list(contacts[0])
    for column in [
        "Record ID",
        "First Name",
        "Last Name",
        "Email",
        "Phone Number",
        "Country/Region",
        "Message",
        "Lifecycle Stage",
        "Create Date",
        "Associated Deal IDs",
        "Title",
        "Number of adults",
    ]:
        assert column in header
    for contact in contacts:
        deal = deals[contact["Associated Deal IDs"]]
        assert deal["Associated Contact IDs"] == contact["Record ID"]
        # Only names reserved for examples (RFC 2606), however mistyped the address is.
        assert "example" in contact["Email"].rsplit("@")[-1], contact["Email"]


def test_calls_are_logged_contact_attempts_on_known_deals(middle):
    calls = rows(middle / CALLS)
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    assert calls
    assert {c["Call outcome"] for c in calls} <= {
        "Connected",
        "No answer",
        "Left voicemail",
        "Busy",
    }
    truth = {r["deal_record_id"]: r for r in rows(middle / TRUTH)}
    for call in calls:
        assert call["Associated Deal IDs"] in deals
        first_attempt = truth[call["Associated Deal IDs"]]["first_contact_attempt_at"]
        assert first_attempt <= call["Activity date"]


def test_the_true_path_enters_stages_in_ladder_order_without_skips(middle, raw):
    ladder = [
        s["name"]
        for s in raw["pipeline"]["stages"]
        if not s.get("milestone") and not s.get("after_won") and s.get("closed") != "lost"
    ]
    true_times = {}
    for change in rows(middle / STAGE_HISTORY):
        if change["true_entered_at"]:
            true_times[change["deal_record_id"], change["crm_stage"]] = change["true_entered_at"]
    for deal in rows(middle / DEALS):
        entered = [true_times.get((deal["Record ID"], s), "") for s in ladder]
        reached = [t for t in entered if t]
        assert entered[: len(reached)] == reached, deal["Record ID"]
        assert reached == sorted(reached), deal["Record ID"]


def test_the_hidden_truth_has_one_row_per_deal_keyed_by_both_record_ids(middle):
    truth = rows(middle / TRUTH)
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    assert len(truth) == len(deals)
    for row in truth:
        assert deals[row["deal_record_id"]]["Associated Contact IDs"] == row["contact_record_id"]
    assert list(truth[0]) == [
        "deal_record_id",
        "contact_record_id",
        "market_group",
        "win_propensity",
        "neglected_lead",
        "first_contact_attempt_at",
        "reached_stage",
        "outcome",
        "won_at",
        "deal_value",
        "itinerary_versions",
        "cancelled_after_won",
        "call_attempts",
        "true_loss_reason",
        "row_kind",
        "duplicate_of_deal_record_id",
        "invalid_email",
        "invalid_phone",
    ]
