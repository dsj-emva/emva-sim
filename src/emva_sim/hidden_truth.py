"""The Hidden truth: what the generator knows about every deal, kept apart from the exports.

hidden-truth.csv has one row per deal; stage-history.csv one row per CRM stage change, with when
it truly happened and when the team recorded it; text.csv one row per piece of text in the exports
(each deal's message, each call's notes, each note, each Closed Lost Reason), with the phrases it
was written from, what was planted in it, and the sentence carrying a planted text signal as it was
written before any abbreviation or typo. Read only when grading Emva.
"""

import csv
from collections.abc import Iterable, Iterator
from pathlib import Path

from emva_sim import effects, ladder
from emva_sim.hubspot import Record, stamp
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.notes import Activities
from emva_sim.phrases import Text
from emva_sim.process import TruePath


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _money(amount: float) -> str:
    return f"{amount:.2f}"


# What the lead is that the exports do not show (issue #6 writes text to match), each with how the
# hidden truth writes it.
HIDDEN_ATTRIBUTES = {
    "budget_per_person_per_night": _money,
    "message_words": str,
    "text_commitment": _yes_no,
    "real_buyer": _yes_no,
}

# A genuine Lead's true path; blank for duplicates and bots, which have none. Between the two
# parts, one term per planted effect that has one, in profile order (true_path_columns).
_PATH_COLUMNS = [
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
    "base_log_odds",
]
_PROPENSITY_COLUMNS = ["high_quality", *HIDDEN_ATTRIBUTES]
_OTHER_COLUMNS = [
    "true_loss_reason",
    "recorded_loss_reason",
    "row_kind",
    "duplicate_of_deal_record_id",
    "invalid_email",
    "invalid_phone",
    "fields_missing_or_wrong",
]


def true_path_columns(p: dict) -> list[str]:
    terms = [f"term_{name}" for name in effects.term_names(p)]
    return [*_PATH_COLUMNS, *terms, *_PROPENSITY_COLUMNS]


def columns(p: dict) -> list[str]:
    return ["deal_record_id", "contact_record_id", *true_path_columns(p), *_OTHER_COLUMNS]


STAGE_HISTORY_COLUMNS = ["deal_record_id", "crm_stage", "true_entered_at", "recorded_entered_at"]
TEXT_COLUMNS = [
    "deal_record_id",
    "text",
    "activity_record_id",
    "language",
    "shape",
    "phrase_ids",
    "prohibited_mentions",
    "fact_differs_from_fields",
    "abbreviated",
    "typo",
    "signal",
]
MESSAGE, CALL_NOTES, NOTE_BODY, CLOSED_LOST_REASON = (
    "message",
    "call notes",
    "note body",
    "closed lost reason",
)


def write(
    folder: Path, p: dict, records: list[Record], paths: list[TruePath], activities: Activities
) -> None:
    _write(folder / "hidden-truth.csv", columns(p), _rows(p, records, paths))
    _write(folder / "stage-history.csv", STAGE_HISTORY_COLUMNS, _stage_history(records))
    _write(folder / "text.csv", TEXT_COLUMNS, _texts(records, activities))


def _write(path: Path, header: list[str], rows: Iterable[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)


def _true_path(lead: Lead, path: TruePath) -> list[str]:
    return [
        lead.market_group.upper(),
        f"{path.propensity.chance:.8g}",
        _yes_no(path.neglected_lead),
        stamp(path.stage_times.get(ladder.CONTACT_ATTEMPTED)),
        path.reached_stage,
        "won" if path.won else "not won",
        stamp(path.stage_times.get(ladder.WON)),
        f"{lead.deal_value:.2f}" if path.quotes else "",
        str(len(path.quotes)),
        _yes_no(bool(path.cancelled_at)),
        str(sum(attempt.channel == "call" for attempt in path.attempts)),
        f"{path.propensity.base_log_odds:.6f}",
        *(f"{term:.6f}" for term in path.propensity.terms.values()),
        _yes_no(path.propensity.high_quality),
        *(write(getattr(lead, name)) for name, write in HIDDEN_ATTRIBUTES.items()),
    ]


def true_path(p: dict, lead: Lead, path: TruePath) -> dict[str, str]:
    """A genuine Lead's true-path columns, by name."""
    return dict(zip(true_path_columns(p), _true_path(lead, path), strict=True))


def _rows(p: dict, records: list[Record], paths: list[TruePath]) -> Iterator[list[str]]:
    deal_of_lead = {
        r.submission.index: r.deal_id for r in records if r.submission.kind == RowKind.LEAD
    }
    for r in records:
        s = r.submission
        genuine = s.kind == RowKind.LEAD
        blank = [""] * len(true_path_columns(p))
        true_path = _true_path(s.lead, paths[s.index]) if genuine else blank
        yield [
            str(r.deal_id),
            str(r.contact_id),
            *true_path,
            r.recorded.true_loss_reason,
            r.recorded.closed_lost_reason,
            s.kind,
            str(deal_of_lead[s.index]) if s.kind == RowKind.DUPLICATE else "",
            *((_yes_no(s.invalid_email), _yes_no(s.invalid_phone)) if genuine else ("", "")),
            ";".join(s.missing_or_wrong),
        ]


def _stage_history(records: list[Record]) -> Iterator[list[str]]:
    for r in records:
        for change in r.recorded.changes:
            yield [str(r.deal_id), change.stage, stamp(change.true_at), stamp(change.recorded_at)]


def _flag(flag: bool | None) -> str:
    return "" if flag is None else _yes_no(flag)


def _text_row(deal_id: int, kind: str, activity: str, text: Text) -> list[str]:
    differs = {None: "", "": "none"}.get(text.fact_differs, text.fact_differs)
    return [
        str(deal_id),
        kind,
        activity,
        text.language,
        text.shape,
        ";".join(text.phrase_ids),
        ";".join(text.mentions),
        differs,
        _flag(text.abbreviated),
        _flag(text.typo),
        text.signal,
    ]


def _texts(records: list[Record], activities: Activities) -> Iterator[list[str]]:
    for r in records:
        yield _text_row(r.deal_id, MESSAGE, "", r.submission.message)
    for call in activities.calls:
        if call.notes:
            yield _text_row(call.deal_id, CALL_NOTES, str(call.record_id), call.notes)
    for note in activities.notes:
        yield _text_row(note.deal_id, NOTE_BODY, str(note.record_id), note.body)
    for deal_id, reason in activities.lost_reasons.items():
        yield _text_row(deal_id, CLOSED_LOST_REASON, "", reason)
