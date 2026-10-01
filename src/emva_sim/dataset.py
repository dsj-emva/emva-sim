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

from emva_sim import hidden_truth, hubspot, intake, leads, messages, profile
from emva_sim.hubspot import Record
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.phrases import Phrases
from emva_sim.process import Process, TruePath
from emva_sim.recording import Recording


@dataclass(frozen=True)
class History:
    start: date = date(2024, 1, 1)
    end: date = date(2025, 12, 31)
    export: date = date(2026, 1, 5)


DEFAULT_HISTORY = History()


def folder_name(setting: str) -> str:
    """A dataset's folder: its setting, with "<range name>@<end>" written as the profile key its
    number is read from."""
    return setting.replace("@", ".")


def leads_and_paths(
    p: dict, rng: Random, history: History = DEFAULT_HISTORY
) -> tuple[list[Lead], list[TruePath]]:
    """Every genuine Lead of the history and its true path, drawn before any mess."""
    drawn = leads.draw_leads(rng, p, history.start, history.end)
    return drawn, Process(p, history.start).paths(rng, drawn)


def generate(
    profile_path: Path, setting: str, seed: int, out: Path, history: History = DEFAULT_HISTORY
) -> Path:
    """Write one dataset to the folder of out named for it, and return that folder."""
    folder = Path(out) / folder_name(setting)
    raw = profile.load(profile_path)
    write(raw, Phrases.load(profile_path, raw), setting, seed, folder, history)
    return folder


def write(
    raw: dict, phrases: Phrases, setting: str, seed: int, folder: Path, history: History
) -> None:
    """Write one dataset into folder, replacing any earlier copy of it.

    The text is written after the true paths, from the profile's phrases and their cached
    variations, so it never changes them either.
    """
    p = profile.resolve(raw, setting)
    rng = Random(seed)
    drawn, paths = leads_and_paths(p, rng, history)
    writer = messages.Writer(p, phrases)
    written = [writer.message(rng, lead) for lead in drawn]
    drawn = [writer.written(lead, text) for lead, text in zip(drawn, written, strict=True)]

    start = datetime.combine(history.start, datetime.min.time())
    after_end = datetime.combine(history.end + timedelta(days=1), datetime.min.time())
    received = intake.submissions(rng, p, drawn, written, writer, start, after_end)
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

    shutil.rmtree(folder, ignore_errors=True)
    hubspot.Export(p, records, history.export).write(folder / "export", rng)
    hidden_truth.write(folder / "hidden-truth", p, records, paths)
