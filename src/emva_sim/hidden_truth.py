"""The Hidden truth: what the generator knows about every deal, kept apart from the exports.

hidden-truth.csv has one row per deal; stage-history.csv one row per CRM stage change, with when
it truly happened and when the team recorded it. Read only when grading Emva.
"""

import csv
from collections.abc import Iterable, Iterator
from pathlib import Path

from emva_sim import ladder
from emva_sim.hubspot import Record, stamp
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.process import RESPONSE_SPEED, TruePath

# The planted effects' terms, in the order of the profile; the proxy trap has none.
TERMS = [
    "budget_floor",
    "no_budget",
    "lead_time_by_season",
    "date_specificity",
    "lead_source",
    "repeat_client",
    "message_length",
    "party_size",
    "phone_given",
    "price_rise",
    "text_commitment",
    "notes_real_buyer",
    RESPONSE_SPEED,
]
# What the lead is that the exports do not show; issue #6 writes text to match.
HIDDEN_ATTRIBUTES = [
    "budget_per_person_per_night",
    "message_words",
    "message_specificity",
    "text_commitment",
    "real_buyer",
]

# A genuine Lead's true path; blank for duplicates and bots, which have none.
TRUE_PATH_COLUMNS = [
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
    *(f"term_{name}" for name in TERMS),
    "high_quality",
    *HIDDEN_ATTRIBUTES,
]
COLUMNS = [
    "deal_record_id",
    "contact_record_id",
    *TRUE_PATH_COLUMNS,
    "true_loss_reason",
    "row_kind",
    "duplicate_of_deal_record_id",
    "invalid_email",
    "invalid_phone",
    "fields_missing_or_wrong",
]
STAGE_HISTORY_COLUMNS = ["deal_record_id", "crm_stage", "true_entered_at", "recorded_entered_at"]


def write(folder: Path, records: list[Record], paths: list[TruePath]) -> None:
    _write(folder / "hidden-truth.csv", COLUMNS, _rows(records, paths))
    _write(folder / "stage-history.csv", STAGE_HISTORY_COLUMNS, _stage_history(records))


def _write(path: Path, header: list[str], rows: Iterable[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)


def _true_path(lead: Lead, path: TruePath) -> list[str]:
    return [
        lead.market_group.upper(),
        f"{path.win_propensity:.8g}",
        _yes_no(path.neglected_lead),
        stamp(path.stage_times.get(ladder.CONTACT_ATTEMPTED)),
        path.reached_stage,
        "won" if path.won else "not won",
        stamp(path.stage_times.get(ladder.WON)),
        f"{lead.deal_value:.2f}" if path.quotes else "",
        str(len(path.quotes)),
        _yes_no(bool(path.cancelled_at)),
        str(sum(attempt.channel == "call" for attempt in path.attempts)),
        f"{path.base_log_odds:.6f}",
        *(f"{path.terms[name]:.6f}" for name in TERMS),
        _yes_no(path.high_quality),
        *(_attribute(getattr(lead, name)) for name in HIDDEN_ATTRIBUTES),
    ]


def true_path(lead: Lead, path: TruePath) -> dict[str, str]:
    """A genuine Lead's true-path columns, by name."""
    return dict(zip(TRUE_PATH_COLUMNS, _true_path(lead, path), strict=True))


def _attribute(value) -> str:
    if isinstance(value, bool):
        return _yes_no(value)
    return f"{value:.2f}" if isinstance(value, float) else str(value)


def _rows(records: list[Record], paths: list[TruePath]) -> Iterator[list[str]]:
    deal_of_lead = {
        r.submission.index: r.deal_id for r in records if r.submission.kind == RowKind.LEAD
    }
    for r in records:
        s = r.submission
        genuine = s.kind == RowKind.LEAD
        true_path = _true_path(s.lead, paths[s.index]) if genuine else [""] * len(TRUE_PATH_COLUMNS)
        yield [
            str(r.deal_id),
            str(r.contact_id),
            *true_path,
            r.recorded.true_loss_reason,
            s.kind,
            str(deal_of_lead[s.index]) if s.kind == RowKind.DUPLICATE else "",
            *((_yes_no(s.invalid_email), _yes_no(s.invalid_phone)) if genuine else ("", "")),
            ";".join(s.missing_or_wrong),
        ]


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _stage_history(records: list[Record]) -> Iterator[list[str]]:
    for r in records:
        for change in r.recorded.changes:
            yield [str(r.deal_id), change.stage, stamp(change.true_at), stamp(change.recorded_at)]
