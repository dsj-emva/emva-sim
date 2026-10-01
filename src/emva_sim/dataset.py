"""One dataset: the exports a sales system would hand over, and the Hidden truth kept apart.

Layout: <out>/<dataset>/export/<variant>/<HubSpot file>.csv and
<out>/<dataset>/hidden-truth/hidden-truth.csv. Everything comes from the profile, the setting and
the seed: no system clock, no global random state.
"""

import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from random import Random

from emva_sim import hubspot, ladder, leads, profile
from emva_sim.hubspot import Record, stamp
from emva_sim.process import Process
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
]
STAGE_HISTORY_COLUMNS = ["deal_record_id", "crm_stage", "true_entered_at", "recorded_entered_at"]


@dataclass(frozen=True)
class History:
    start: date = date(2024, 1, 1)
    end: date = date(2025, 12, 31)
    export: date = date(2026, 1, 5)


DEFAULT_HISTORY = History()


def _truth_row(r: Record) -> list[str]:
    path = r.path
    return [
        str(r.deal_id),
        str(r.contact_id),
        r.lead.market_group.upper(),
        f"{path.win_propensity:.6f}",
        "yes" if path.neglected_lead else "no",
        stamp(path.stage_times.get(ladder.CONTACT_ATTEMPTED)),
        path.reached_stage,
        "won" if path.won else "not won",
        stamp(path.stage_times.get(ladder.WON)),
        f"{r.lead.deal_value:.2f}" if path.quotes else "",
        str(len(path.quotes)),
        "yes" if path.cancelled_at else "no",
        str(sum(attempt.channel == "call" for attempt in path.attempts)),
        r.recorded.true_loss_reason,
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
    deal_ids = hubspot.record_ids(rng, len(drawn), hubspot.DEAL_RECORD_IDS_FROM)
    contact_ids = hubspot.record_ids(rng, len(drawn), hubspot.CONTACT_RECORD_IDS_FROM)
    recording = Recording(p, rng)
    recorded = [recording.lead(lead, path) for lead, path in zip(drawn, paths, strict=True)]
    records = [
        Record(*row) for row in zip(deal_ids, contact_ids, drawn, paths, recorded, strict=True)
    ]

    folder = Path(out) / name(p, setting, seed)
    shutil.rmtree(folder, ignore_errors=True)
    hubspot.Export(p, records, history.export).write(folder / "export", rng)
    truth = folder / "hidden-truth"
    hubspot.write_csv(truth / "hidden-truth.csv", HIDDEN_TRUTH_COLUMNS, map(_truth_row, records))
    hubspot.write_csv(truth / "stage-history.csv", STAGE_HISTORY_COLUMNS, _stage_history(records))
    return folder


def _stage_history(records: list[Record]) -> Iterator[list[str]]:
    for r in records:
        for change in r.recorded.changes:
            yield [str(r.deal_id), change.stage, stamp(change.true_at), stamp(change.recorded_at)]
