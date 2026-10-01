"""Sales notes and Closed Lost Reasons: what the sales team writes about each Lead.

A Lead with a Contact attempt has notes at notes.attempted_with_any_note: one at its first Contact
attempt, one at Engaged (what the first conversation found, and what it showed about the Lead),
one per itinerary version sent, and a note on each call the team logged. The notes at Engaged and
on the first itinerary say by their content, never by a keyword, whether the Lead is a real buyer
(effects.notes_real_buyer). Notes carry the team's abbreviations and typos at their shares
(notes-and-loss-reasons.md §2). A Lost deal's recorded reason is written as the team types it.
Only what was written before the export date is kept.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from random import Random

from emva_sim import hubspot, intake, ladder
from emva_sim.hubspot import Record
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.messages import ENGLISH, Writer
from emva_sim.phrases import Phrases, Text, render
from emva_sim.process import ContactAttempt, TruePath

CONNECTED = "Connected"
# HubSpot's default outcomes of a call that did not connect, each with its note group.
UNCONNECTED = {"No answer": "no_answer", "Left voicemail": "left_voicemail", "Busy": "busy"}
NOTE_RECORD_IDS_FROM = 40_000_000_000
# The note on each itinerary version after the first: logistics only, saying nothing of the Lead.
REVISED = "revised"


@dataclass(frozen=True)
class Call:
    record_id: int
    at: datetime
    deal_id: int
    outcome: str
    notes: Text | None


@dataclass(frozen=True)
class Note:
    record_id: int
    at: datetime
    deal_id: int
    body: Text


@dataclass(frozen=True)
class Activities:
    """The logged calls, the notes and the Closed Lost Reasons, as the team wrote them."""

    calls: list[Call]
    notes: list[Note]
    lost_reasons: dict[int, Text]


class Notes:
    def __init__(self, p: dict, phrases: Phrases, writer: Writer, rng: Random):
        self.p = p
        self.phrases = phrases
        self.writer = writer
        self.rng = rng
        self.abbreviations = [
            (re.compile(rf"\b{re.escape(full)}\b", re.IGNORECASE), short)
            for full, short in p["text"]["abbreviations"]
        ]

    def write(self, records: list[Record], paths: list[TruePath], until: datetime) -> Activities:
        calls, notes, lost = [], [], {}
        for r in records:
            s = r.submission
            if r.recorded.closed_lost_reason:
                lost[r.deal_id] = self._loss_reason(r.recorded.closed_lost_reason)
            if s.kind != RowKind.LEAD:
                continue
            path = paths[s.index]
            writes = (
                not path.neglected_lead
                and self.rng.random() < self.p["notes"]["attempted_with_any_note"]
            )
            values = self.writer.values(self.rng, s.lead, ENGLISH) if writes else {}
            for attempt in r.recorded.calls:
                calls.append(self._call(r, attempt, writes, values))
            if writes:
                written = self._notes(path, s.lead, values)
                notes.extend((at, r.deal_id, body) for at, body in written)
        calls = sorted((c for c in calls if c[0] < until), key=lambda c: (c[0], c[1]))
        notes = sorted((n for n in notes if n[0] < until), key=lambda n: (n[0], n[1]))
        call_ids = hubspot.record_ids(self.rng, len(calls), hubspot.CALL_RECORD_IDS_FROM)
        note_ids = hubspot.record_ids(self.rng, len(notes), NOTE_RECORD_IDS_FROM)
        return Activities(
            [Call(i, *c) for i, c in zip(call_ids, calls, strict=True)],
            [Note(i, *n) for i, n in zip(note_ids, notes, strict=True)],
            lost,
        )

    def _call(self, r: Record, attempt: ContactAttempt, writes: bool, values: dict) -> tuple:
        outcome = CONNECTED if attempt.connected else self.rng.choice(sorted(UNCONNECTED))
        note = None
        if writes:
            if attempt.connected:
                note = self._discovery(r.submission.lead, values)
            else:
                note = self._note([f"notes.call.{UNCONNECTED[outcome]}"], values)
        return attempt.at, r.deal_id, outcome, note

    def _notes(self, path: TruePath, lead: Lead, values: dict) -> list[tuple[datetime, Text]]:
        first = path.attempts[0]
        written = [(first.at, self._note([f"notes.first_attempt.{first.channel}"], values))]
        engaged = path.stage_times.get(ladder.ENGAGED)
        if engaged:
            written.append((engaged, self._discovery(lead, values)))
        for version, (at, _) in enumerate(path.quotes):
            said = _buyer(lead) if version == 0 else REVISED
            written.append((at, self._note([f"notes.follow_up.{said}"], values)))
        return written

    def _discovery(self, lead: Lead, values: dict) -> Text:
        return self._note(["notes.recap", f"notes.discovery.{_buyer(lead)}"], values)

    def _note(self, groups: list[str], values: dict) -> Text:
        """A note of one phrase from each group, abbreviated and with a typo at their shares."""
        picked = []
        for group in groups:
            usable = [ph for ph in self.phrases.group(group) if ph.slots <= set(values)]
            phrase = self.rng.choice(usable)
            picked.append((phrase.id, render(self.rng.choice(phrase.options), values)))
        text = " ".join(t for _, t in picked)
        abbreviated = False
        if self.rng.random() < self.p["notes"]["with_abbreviation"]:
            short = self._abbreviated(text)
            abbreviated, text = short != text, short
        typo = False
        if self.rng.random() < self.p["notes"]["with_typo"]:
            slipped = self._typo(text)
            typo, text = slipped != text, slipped
        return Text(
            text, tuple(pid for pid, _ in picked), ENGLISH, abbreviated=abbreviated, typo=typo
        )

    def _abbreviated(self, text: str) -> str:
        for pattern, short in self.abbreviations:
            text = pattern.sub(short, text)
        return text

    def _typo(self, text: str) -> str:
        """One word of four letters or more typed wrongly."""
        found = list(re.finditer(r"[A-Za-z]{4,}", text))
        if not found:
            return text
        word = self.rng.choice(found)
        return text[: word.start()] + intake.slip(self.rng, word.group()) + text[word.end() :]

    def _loss_reason(self, recorded: str) -> Text:
        phrase = self.rng.choice(self.phrases.group(f"loss_reason.{recorded}"))
        return Text(self.rng.choice(phrase.options), (phrase.id,), ENGLISH)


def _buyer(lead: Lead) -> str:
    return "real_buyer" if lead.real_buyer else "not_real_buyer"
