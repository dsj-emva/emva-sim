"""One dataset: the exports a sales system would hand over, and the Hidden truth kept apart.

Layout: <out>/<dataset>/export/<variant>/<HubSpot file>.csv, and <out>/<dataset>/hidden-truth/
(see hidden_truth.py). Everything comes from the profile, the setting and the seed: no system
clock, no global random state. The Leads and their true paths are drawn first, so the mess drawn
after them never changes them.
"""

import shutil
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

from emva_sim import hidden_truth, hubspot, intake, leads, profile
from emva_sim.hubspot import Record
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.process import Process, TruePath
from emva_sim.recording import Recording


@dataclass(frozen=True)
class History:
    start: date = date(2024, 1, 1)
    end: date = date(2025, 12, 31)
    export: date = date(2026, 1, 5)


DEFAULT_HISTORY = History()


def name(p: dict, setting: str, seed: int) -> str:
    return f"{p['name']}-{setting}-seed-{seed}"


def leads_and_paths(
    p: dict, rng: Random, history: History = DEFAULT_HISTORY
) -> tuple[list[Lead], list[TruePath]]:
    """Every genuine Lead of the history and its true path, drawn before any mess."""
    drawn = leads.draw_leads(rng, p, history.start, history.end)
    return drawn, Process(p, history.start).paths(rng, drawn)


def generate(
    profile_path: Path, setting: str, seed: int, out: Path, history: History = DEFAULT_HISTORY
) -> Path:
    """Write one dataset, replacing any earlier copy of it, and return its folder."""
    p = profile.resolve(profile.load(profile_path), setting)
    rng = Random(seed)
    drawn, paths = leads_and_paths(p, rng, history)

    start = datetime.combine(history.start, datetime.min.time())
    after_end = datetime.combine(history.end + timedelta(days=1), datetime.min.time())
    received = intake.submissions(rng, p, drawn, start, after_end)
    deal_ids = hubspot.record_ids(rng, len(received), hubspot.DEAL_RECORD_IDS_FROM)
    new_contacts = sum(s.new_contact for s in received)
    contact_ids = iter(hubspot.record_ids(rng, new_contacts, hubspot.CONTACT_RECORD_IDS_FROM))
    contact_of_lead = {}
    recording = Recording(p, rng)
    records = []
    for deal_id, s in zip(deal_ids, received, strict=True):
        contact_id = next(contact_ids) if s.new_contact else contact_of_lead[s.index]
        if s.kind == RowKind.LEAD:
            contact_of_lead[s.index] = contact_id
            owner, recorded = paths[s.index].owner, recording.lead(paths[s.index])
        else:
            owner, recorded = rng.choice(p["team"]["owners"]), recording.not_a_lead(s.submitted_at)
        records.append(Record(deal_id, contact_id, owner, s, recorded))

    folder = Path(out) / name(p, setting, seed)
    shutil.rmtree(folder, ignore_errors=True)
    hubspot.Export(p, records, history.export).write(folder / "export", rng)
    hidden_truth.write(folder / "hidden-truth", records, paths)
    return folder
