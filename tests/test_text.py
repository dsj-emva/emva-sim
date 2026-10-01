"""The text in the exports, on simulated data: the enquiry message, Sales notes, Closed Lost
Reasons and bots' spam, written from the phrase bank and the echoed test cache (echo_model).

One fixed seed, six months of leads, exported long after the last one so their notes are in.
"""

import math
import re
import shutil
from collections import defaultdict
from datetime import date
from random import Random

import pytest
import separability
from conftest import REAL_PROFILE, STAGES, assert_rate, ends, kinds, number, raw, resolved, rows

from emva_sim import dataset, datasets, messages, phrases
from emva_sim.hidden_truth import CALL_NOTES, CLOSED_LOST_REASON, NOTE_BODY
from emva_sim.hidden_truth import MESSAGE as MESSAGE_TEXT
from emva_sim.intake import RowKind
from emva_sim.phrases import MissingVariations

HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2025, 12, 31))
EXPORT = "export/with-calls-and-notes"
CONTACTS = f"{EXPORT}/hubspot-crm-exports-all-contacts-2025-12-31.csv"
DEALS = f"{EXPORT}/hubspot-crm-exports-safari-enquiries-2025-12-31.csv"
CALLS = f"{EXPORT}/hubspot-crm-exports-all-calls-2025-12-31.csv"
NOTES = f"{EXPORT}/hubspot-crm-exports-all-notes-2025-12-31.csv"
TEXTS = "hidden-truth/text.csv"
MESSAGE = "Message"


@pytest.fixture(scope="module")
def generated(generate):
    return lambda setting: generate(setting, HISTORY)


@pytest.fixture(scope="module")
def middle(generated):
    return generated("middle")


def message_of_deal(folder):
    """Each deal's contact's Message, by deal Record ID."""
    return {
        deal: contact[MESSAGE]
        for contact in rows(folder / CONTACTS)
        for deal in contact["Associated Deal IDs"].split(";")
    }


def test_each_leads_contact_shows_a_message_of_its_hidden_number_of_words(middle):
    messages = message_of_deal(middle)
    leads = kinds(middle, RowKind.LEAD)
    for row in leads:
        assert phrases.words(messages[row["deal_record_id"]]) == int(row["message_words"]), row
    written = [row for row in leads if messages[row["deal_record_id"]]]
    blank = number("middle", "form.message.blank_or_token")
    assert len(written) > (1 - blank) * len(leads)


def missing_cache_profile(tmp_path):
    for name in ("planned-hospitality.toml", "planned-hospitality.phrases.toml"):
        shutil.copy(REAL_PROFILE.parent / name, tmp_path / name)
    return tmp_path / "planned-hospitality.toml"


def test_a_phrase_with_no_cached_variations_stops_generation_naming_the_command(tmp_path):
    copy = missing_cache_profile(tmp_path)
    with pytest.raises(MissingVariations, match="make vary-phrases"):
        dataset.generate(copy, "middle", seed=1, out=tmp_path / "out", history=HISTORY)
    assert not (tmp_path / "out").exists()
    with pytest.raises(MissingVariations):
        datasets.write_all(copy, tmp_path / "sweep", history=HISTORY)
    assert not (tmp_path / "sweep").exists()


def test_one_missing_variation_is_enough_to_stop_generation(tmp_path, test_profile):
    folder = tmp_path / "p"
    shutil.copytree(test_profile.parent, folder)
    cache_path = folder / "planned-hospitality.variations.json"
    cache = phrases.read_cache(cache_path, "echo")
    cache["phrases"].pop(sorted(cache["phrases"])[0])
    phrases.write_cache(cache_path, cache)
    with pytest.raises(MissingVariations, match="1 phrases"):
        dataset.generate(
            folder / test_profile.name, "middle", seed=1, out=tmp_path, history=HISTORY
        )


@pytest.mark.parametrize("setting", ["middle", "mess.bot_or_spam@high"])
def test_the_profiles_share_of_bots_write_spam(generated, setting):
    folder = generated(setting)
    messages = message_of_deal(folder)
    bots = kinds(folder, RowKind.BOT)
    links = number(setting, "text.spam_links")
    spam = [row for row in bots if any(link in messages[row["deal_record_id"]] for link in links)]
    # Gibberish has no link: a third of the spam, by kind.
    share = number(setting, "mess.bot_spam_message") * 2 / 3
    assert_rate(len(spam), len(bots), share)


def texts(folder, kind=None):
    found = rows(folder / TEXTS)
    return [t for t in found if kind is None or t["text"] == kind]


def notes_of_deal(folder):
    """Each deal's Sales notes from the hidden truth: call notes and note bodies."""
    by_deal = defaultdict(list)
    for t in texts(folder):
        if t["text"] in (CALL_NOTES, NOTE_BODY):
            by_deal[t["deal_record_id"]].append(t)
    return by_deal


def attempted(folder):
    return [r for r in kinds(folder, RowKind.LEAD) if r["first_contact_attempt_at"]]


@pytest.mark.parametrize("setting", ends("notes.attempted_with_any_note"))
def test_the_profiles_share_of_attempted_leads_have_sales_notes(generated, setting):
    folder = generated(setting)
    noted = notes_of_deal(folder)
    leads = attempted(folder)
    with_notes = [r for r in leads if noted[r["deal_record_id"]]]
    assert_rate(len(with_notes), len(leads), number(setting, "notes.attempted_with_any_note"))
    neglected = [r for r in kinds(folder, RowKind.LEAD) if not r["first_contact_attempt_at"]]
    assert not [r for r in neglected if noted[r["deal_record_id"]]]


def groups(text_row):
    return {pid.split("#")[0] for pid in text_row["phrase_ids"].split(";") if pid}


def engaged_before_export(folder):
    """The deals that truly entered In Discussion (Engaged) before the export."""
    return {
        c["deal_record_id"]
        for c in rows(folder / STAGES)
        if c["crm_stage"] == "In Discussion"
        and c["true_entered_at"]
        and c["true_entered_at"] < "2025-12-31"
    }


def test_notes_say_whether_the_lead_is_a_real_buyer_only_from_engaged_on(middle):
    noted = notes_of_deal(middle)
    engaged = engaged_before_export(middle)
    checked = 0
    for row in attempted(middle):
        if not noted[row["deal_record_id"]]:
            continue
        said = set().union(*(groups(t) for t in noted[row["deal_record_id"]]))
        meaning = {
            g.rsplit(".", 1)[1]
            for g in said
            if (".discovery." in g or ".follow_up." in g) and not g.endswith(".revised")
        }
        if row["deal_record_id"] in engaged:
            assert meaning == {"real_buyer" if row["real_buyer"] == "yes" else "not_real_buyer"}
            checked += 1
        else:
            assert not meaning, row
    assert checked


@pytest.mark.parametrize(
    ("setting", "flag", "share"),
    [
        *[(s, "abbreviated", "notes.with_abbreviation") for s in ends("notes.with_abbreviation")],
        *[(s, "typo", "notes.with_typo") for s in ends("notes.with_typo")],
    ],
)
def test_notes_carry_abbreviations_and_typos_at_their_shares(generated, setting, flag, share):
    notes = [t for t in texts(generated(setting)) if t["text"] in (CALL_NOTES, NOTE_BODY)]
    marked = sum(t[flag] == "yes" for t in notes)
    assert_rate(marked, len(notes), number(setting, share))


def test_the_notes_export_holds_each_note_on_its_deal_and_contact(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    exported = rows(middle / NOTES)
    assert exported
    assert list(exported[0]) == [
        "Record ID",
        "Activity date",
        "Note body",
        "Associated Contact",
        "Associated Contact IDs",
        "Associated Deal",
        "Associated Deal IDs",
    ]
    truth = {t["activity_record_id"]: t for t in texts(middle, NOTE_BODY)}
    assert set(truth) == {n["Record ID"] for n in exported}
    for note in exported:
        deal = deals[note["Associated Deal IDs"]]
        assert deal["Associated Contact IDs"] == note["Associated Contact IDs"]
        assert note["Note body"]
        assert note["Activity date"] < "2025-12-31"


def test_a_logged_call_has_notes_only_on_a_lead_with_notes_and_says_what_happened(middle):
    calls = rows(middle / CALLS)
    truth = {t["activity_record_id"]: t for t in texts(middle, CALL_NOTES)}
    assert {c["Record ID"] for c in calls if c["Call notes"]} == set(truth)
    for call in calls:
        if call["Call notes"]:
            said = groups(truth[call["Record ID"]])
            if call["Call outcome"] == "Connected":
                assert said == {"notes.recap"}
            else:
                assert said == {f"notes.call.{call['Call outcome'].lower().replace(' ', '_')}"}


def test_a_closed_lost_reason_is_written_from_the_reason_the_team_recorded(middle):
    truth = {r["deal_record_id"]: r for r in rows(middle / "hidden-truth/hidden-truth.csv")}
    reasons = {t["deal_record_id"]: t for t in texts(middle, CLOSED_LOST_REASON)}
    lost = [d for d in rows(middle / DEALS) if d["Deal Stage"] == "Lost"]
    assert lost
    for deal in lost:
        recorded = truth[deal["Record ID"]]["recorded_loss_reason"]
        assert bool(deal["Closed Lost Reason"]) == bool(recorded), deal["Record ID"]
        if recorded:
            assert groups(reasons[deal["Record ID"]]) == {f"loss_reason.{recorded}"}
    shown = {d["Closed Lost Reason"] for d in lost if d["Closed Lost Reason"]}
    assert len(shown) > len({truth[d["Record ID"]]["recorded_loss_reason"] for d in lost})


def test_no_phrase_id_or_hidden_text_column_reaches_an_export(middle):
    for path in sorted((middle / "export").rglob("*.csv")):
        content = path.read_text(encoding="utf-8")
        assert not re.search(r"[a-z_]+\.[a-z_. ]+#\d", content), path
        header = set(rows(path)[0])
        assert not header & {"phrase_ids", "prohibited_mentions", "fact_differs_from_fields"}


def written_messages(folder):
    """Each genuine Lead's written message (not blank or a token) as its contact shows it, with
    its hidden truth and the text's."""
    messages = message_of_deal(folder)
    truth = {t["deal_record_id"]: t for t in texts(folder, MESSAGE_TEXT)}
    return [
        (messages[r["deal_record_id"]], r, truth[r["deal_record_id"]])
        for r in kinds(folder, RowKind.LEAD)
        if truth[r["deal_record_id"]]["shape"] not in ("blank", "token")
    ]


def test_every_lead_with_a_decision_made_and_no_other_writes_one_in_its_message(middle):
    found = written_messages(middle)
    for _, row, text in found:
        committed = {g for g in groups(text) if g.endswith(".commitment")}
        assert bool(committed) == (row["text_commitment"] == "yes"), row["deal_record_id"]
    assert sum(row["text_commitment"] == "yes" for _, row, _ in found)


# The signal's share at both ends, and every range at each end together.
# The middle, each text effect's ends one at a time, and every range at each end together.
TEXT_EFFECTS = [
    "effects.text_commitment.share_of_leads",
    "effects.text_commitment.odds_ratio",
    "effects.notes_real_buyer.odds_ratio",
    "notes.real_buyer_share",
]
SEPARABILITY_SETTINGS = [
    "middle",
    *(f"{name}@{end}" for name in TEXT_EFFECTS for end in ("low", "high")),
    "all-low",
    "all-high",
]
# Enough Leads at every volume that one phrase picked by chance is not mistaken for a rule.
SEPARABILITY_LEADS = 4800


def separability_history(setting):
    """A history ending where HISTORY does, long enough for SEPARABILITY_LEADS Leads."""
    months = max(6, math.ceil(SEPARABILITY_LEADS / number(setting, "volume.leads_per_month")))
    first = 2024 * 12 + 6 - months
    start = date(first // 12, first % 12 + 1, 1)
    return dataset.History(start=start, end=HISTORY.end, export=HISTORY.export)


@pytest.mark.parametrize("setting", SEPARABILITY_SETTINGS)
def test_no_word_or_short_phrase_tells_a_decision_made_from_none(generate, setting):
    folder = generate(setting, separability_history(setting))
    found = [(text, row["text_commitment"] == "yes") for text, row, _ in written_messages(folder)]
    assert separability.separating(found) == [], separability.strongest(found)


def engaged_notes(folder):
    """Each genuine Lead's Sales notes, joined, for the Leads with notes that reached Engaged
    before the export, and whether it is a real buyer."""
    exported = {c["Record ID"]: c["Call notes"] for c in rows(folder / CALLS)}
    exported |= {n["Record ID"]: n["Note body"] for n in rows(folder / NOTES)}
    noted = notes_of_deal(folder)
    engaged = engaged_before_export(folder)
    return [
        (
            " ".join(exported[t["activity_record_id"]] for t in noted[r["deal_record_id"]]),
            r["real_buyer"] == "yes",
        )
        for r in kinds(folder, RowKind.LEAD)
        if r["deal_record_id"] in engaged and noted[r["deal_record_id"]]
    ]


@pytest.mark.parametrize("setting", SEPARABILITY_SETTINGS)
def test_no_word_or_short_phrase_in_the_notes_tells_a_real_buyer_from_the_rest(generate, setting):
    found = engaged_notes(generate(setting, separability_history(setting)))
    assert sum(flag for _, flag in found) >= 200
    assert separability.separating(found) == [], separability.strongest(found)


def leads_of_deals(folder, setting):
    """Each genuine Lead by its deal Record ID. The Leads are drawn first, from the seed, so
    drawing them again gives them; the hidden truth lists them in the order they were drawn."""
    p = resolved(setting)
    drawn, _ = dataset.leads_and_paths(p, Random(1), HISTORY)
    rows_of_leads = kinds(folder, RowKind.LEAD)
    assert len(rows_of_leads) == len(drawn)
    return {r["deal_record_id"]: lead for r, lead in zip(rows_of_leads, drawn, strict=True)}


@pytest.mark.parametrize("setting", ["middle", "all-high"])
def test_no_message_or_note_says_what_the_leads_fields_contradict(generated, setting):
    folder = generated(setting)
    p = resolved(setting)
    by_deal = leads_of_deals(folder, setting)
    bank = phrases.load_bank(phrases.paths(REAL_PROFILE, raw())[0])
    requires = {phrase.id: phrase.requires for phrase in phrases.bank_phrases(bank)}
    checked = 0
    for t in texts(folder):
        lead = by_deal.get(t["deal_record_id"])
        if lead is None or t["text"] == CLOSED_LOST_REASON:
            continue
        known = messages.facts(p, lead)
        for pid in filter(None, t["phrase_ids"].split(";")):
            if pid.startswith(("message.", "notes.")):
                assert requires[pid] <= known, (pid, sorted(requires[pid] - known), t)
                checked += bool(requires[pid])
    assert checked > 50
