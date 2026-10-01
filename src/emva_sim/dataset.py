"""One dataset: the exports a sales system would hand over, and the Hidden truth kept apart.

Layout: <out>/<dataset>/export/<variant>/<HubSpot file>.csv, and in <out>/<dataset>/hidden-truth/
hidden-truth.csv (one row per deal) and stage-history.csv (each CRM stage change, true and as
recorded). Everything comes from the profile, the setting and the seed: no system clock, no global
random state. The Leads and their true paths are drawn first, so the mess drawn after them never
changes them.
"""

import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

from emva_sim import hubspot, intake, ladder, leads, profile
from emva_sim.hubspot import Record, stamp
from emva_sim.leads import Lead
from emva_sim.process import Process, TruePath
from emva_sim.recording import Recording

HIDDEN_TRUTH_COLUMNS = [
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
]
STAGE_HISTORY_COLUMNS = ["deal_record_id", "crm_stage", "true_entered_at", "recorded_entered_at"]
# The columns from market_group to call_attempts hold a genuine Lead's true path.
LEAD_COLUMNS = HIDDEN_TRUTH_COLUMNS.index("true_loss_reason") - 2


@dataclass(frozen=True)
class History:
    start: date = date(2024, 1, 1)
    end: date = date(2025, 12, 31)
    export: date = date(2026, 1, 5)


DEFAULT_HISTORY = History()


def _lead_columns(lead: Lead, path: TruePath) -> list[str]:
    return [
        lead.market_group.upper(),
        f"{path.win_propensity:.6f}",
        "yes" if path.neglected_lead else "no",
        stamp(path.stage_times.get(ladder.CONTACT_ATTEMPTED)),
        path.reached_stage,
        "won" if path.won else "not won",
        stamp(path.stage_times.get(ladder.WON)),
        f"{lead.deal_value:.2f}" if path.quotes else "",
        str(len(path.quotes)),
        "yes" if path.cancelled_at else "no",
        str(sum(attempt.channel == "call" for attempt in path.attempts)),
    ]


def name(p: dict, setting: str, seed: int) -> str:
    return f"{p['name']}-{setting}-seed-{seed}"


def generate(
    profile_path: Path, setting: str, seed: int, out: Path, history: History = DEFAULT_HISTORY
) -> Path:
    """Write one dataset, replacing any earlier copy of it, and return its folder."""
    p = profile.resolve(profile.load(profile_path), setting)
    rng = Random(seed)
    drawn = leads.draw_leads(rng, p, history.start, history.end)
    process = Process(p)
    paths = [process.path(rng, lead) for lead in drawn]

    start = datetime.combine(history.start, datetime.min.time())
    after_end = datetime.combine(history.end + timedelta(days=1), datetime.min.time())
    received = intake.submissions(rng, p, drawn, start, after_end)
    deal_ids = hubspot.record_ids(rng, len(received), hubspot.DEAL_RECORD_IDS_FROM)
    contact_ids = hubspot.record_ids(rng, len(received), hubspot.CONTACT_RECORD_IDS_FROM)
    recording = Recording(p, rng)
    records = []
    for deal_id, contact_id, s in zip(deal_ids, contact_ids, received, strict=True):
        if s.kind == intake.LEAD:
            owner, recorded = paths[s.lead].owner, recording.lead(drawn[s.lead], paths[s.lead])
        else:
            owner, recorded = rng.choice(p["team"]["owners"]), recording.not_a_lead(s.submitted_at)
        records.append(Record(deal_id, contact_id, owner, s, recorded))

    folder = Path(out) / name(p, setting, seed)
    shutil.rmtree(folder, ignore_errors=True)
    hubspot.Export(p, records, history.export).write(folder / "export", rng)
    truth = folder / "hidden-truth"
    rows = _truth_rows(records, drawn, paths)
    hubspot.write_csv(truth / "hidden-truth.csv", HIDDEN_TRUTH_COLUMNS, rows)
    hubspot.write_csv(truth / "stage-history.csv", STAGE_HISTORY_COLUMNS, _stage_history(records))
    return folder


def _truth_rows(
    records: list[Record], drawn: list[Lead], paths: list[TruePath]
) -> Iterator[list[str]]:
    """One row per deal. Only a genuine Lead has a true path and an Outcome."""
    deal_of_lead = {
        r.submission.lead: r.deal_id for r in records if r.submission.kind == intake.LEAD
    }
    for r in records:
        s = r.submission
        genuine = s.kind == intake.LEAD
        lead_columns = (
            _lead_columns(drawn[s.lead], paths[s.lead]) if genuine else [""] * LEAD_COLUMNS
        )
        yield [
            str(r.deal_id),
            str(r.contact_id),
            *lead_columns,
            r.recorded.true_loss_reason,
            s.kind,
            str(deal_of_lead[s.lead]) if s.kind == intake.DUPLICATE else "",
        ]


def _stage_history(records: list[Record]) -> Iterator[list[str]]:
    for r in records:
        for change in r.recorded.changes:
            yield [str(r.deal_id), change.stage, stamp(change.true_at), stamp(change.recorded_at)]
