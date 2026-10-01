"""Sales notes and Closed Lost Reasons: what the sales team writes about each Lead.

A Lead with a Contact attempt has notes at notes.attempted_with_any_note: one at its first Contact
attempt, one at Engaged (what the first conversation found, and what it showed about the Lead),
one per itinerary version sent, and a note on each call the team logged. The notes at Engaged and
on the first itinerary say by their content, never by a keyword, whether the Lead is a real buyer
(effects.notes_real_buyer). Notes carry the team's abbreviations and typos at their shares
(notes-and-loss-reasons.md §2). A Lost deal's recorded reason is written as the team types it.
Only what was written before the export date is kept.
"""

import functools
import re
from dataclasses import dataclass, replace
from datetime import datetime
from random import Random

from emva_sim import hubspot, intake, ladder
from emva_sim.hubspot import Record
from emva_sim.intake import RowKind
from emva_sim.leads import Lead
from emva_sim.messages import ENGLISH, Writer, facts
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
    at: datetime
    deal_id: int
    outcome: str
    notes: Text | None
    record_id: int = 0


@dataclass(frozen=True)
class Note:
    at: datetime
    deal_id: int
    body: Text
    record_id: int = 0


@dataclass(frozen=True)
class Activities:
    """The logged calls, the notes and the Closed Lost Reasons, as the team wrote them."""

    calls: list[Call]
    notes: list[Note]
    lost_reasons: dict[int, Text]


class Notes:
    def __init__(self, p: dict, phrases: Phrases, writer: Writer, rng: Random):
        self.p = p
        self.settings = p["notes"]
        self.text = p["text"]
        self.phrases = phrases
        self.writer = writer
        self.rng = rng
        self.abbreviations = [
            (re.compile(rf"\b{re.escape(full)}\b", re.IGNORECASE), short)
            for full, short in self.text["abbreviations"]
        ]
        short_forms = [short for _, short in self.text["abbreviations"]] + self.text["shorthand"]
        self.shorthand = re.compile(
            "|".join(rf"(?<![\w/]){re.escape(short)}(?![\w/])" for short in short_forms)
        )

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
                and self.rng.random() < self.settings["attempted_with_any_note"]
            )
            lead = _Noted(s.lead, facts(self.p, s.lead), self._values(s.lead) if writes else {})
            for attempt in r.recorded.calls:
                calls.append(self._call(r.deal_id, attempt, writes, lead))
            if writes:
                notes.extend(Note(at, r.deal_id, body) for at, body in self._notes(path, lead))
        calls = sorted((c for c in calls if c.at < until), key=lambda c: (c.at, c.deal_id))
        notes = sorted((n for n in notes if n.at < until), key=lambda n: (n.at, n.deal_id))
        call_ids = hubspot.record_ids(self.rng, len(calls), hubspot.CALL_RECORD_IDS_FROM)
        note_ids = hubspot.record_ids(self.rng, len(notes), NOTE_RECORD_IDS_FROM)
        return Activities(
            [replace(c, record_id=i) for i, c in zip(call_ids, calls, strict=True)],
            [replace(n, record_id=i) for i, n in zip(note_ids, notes, strict=True)],
            lost,
        )

    def _values(self, lead: Lead) -> dict:
        """The slots a note can fill: the message's, with the park perhaps misspelt and the
        budget written as the team writes money."""
        values = self.writer.values(self.rng, lead, ENGLISH)
        if "park" in values:
            values["park"] = self.rng.choice(
                [values["park"], *self.text["park_misspellings"].get(values["park"], [])]
            )
        if lead.states_budget:
            amount = self.text["budget_rounded_to"] * round(
                lead.budget_per_person / self.text["budget_rounded_to"]
            )
            written = self.rng.choice(self.text["note_money"])
            values["budget"] = written.format(thousands=round(amount / 1000), amount=f"{amount:,}")
        return values

    def _call(self, deal_id: int, attempt: ContactAttempt, writes: bool, lead: "_Noted") -> Call:
        outcome = CONNECTED if attempt.connected else self.rng.choice(sorted(UNCONNECTED))
        note = None
        if writes:
            if attempt.connected:
                note = self._discovery(lead)
            else:
                note = self._note([f"notes.call.{UNCONNECTED[outcome]}"], lead)
        return Call(attempt.at, deal_id, outcome, note)

    def _notes(self, path: TruePath, lead: "_Noted") -> list[tuple[datetime, Text]]:
        first = path.attempts[0]
        written = [(first.at, self._note([f"notes.first_attempt.{first.channel}"], lead))]
        engaged = path.stage_times.get(ladder.ENGAGED)
        if engaged:
            written.append((engaged, self._discovery(lead)))
        for version, (at, _) in enumerate(path.quotes):
            if version == 0:
                note = self._note([f"notes.follow_up.{_buyer(lead.lead)}"], lead, signal=0)
            else:
                note = self._note([f"notes.follow_up.{REVISED}"], lead)
            written.append((at, note))
        return written

    def _discovery(self, lead: "_Noted") -> Text:
        """What the first conversation found, as a short recap or, at the profile's share, a
        long paragraph, and then what it showed about the Lead."""
        long = self.rng.random() < self.settings["long_discovery_share"]
        recap = "notes.discovery_call" if long else "notes.recap"
        return self._note([recap, f"notes.discovery.{_buyer(lead.lead)}"], lead, signal=1)

    def _note(self, groups: list[str], lead: "_Noted", signal: int | None = None) -> Text:
        """A note of one phrase from each group the Lead fits, abbreviated and with a typo at
        their shares; signal is the place of the phrase that carries notes_real_buyer. A note
        the team does not abbreviate uses no shorthand at all; one it does, uses shorthand where
        its phrase has an expression to shorten or is written in shorthand."""
        abbreviates = self.rng.random() < self.settings["with_abbreviation"]
        picked = []
        for group in groups:
            usable = [
                ph
                for ph in self.phrases.group(group)
                if ph.slots <= set(lead.values) and ph.requires <= lead.facts
            ]
            options = [
                (ph, option)
                for ph in usable
                for option in ph.options
                if abbreviates or not self._has_shorthand(option)
            ]
            phrase, option = self.rng.choice(options)
            picked.append((phrase.id, render(option, lead.values)))
        text = " ".join(t for _, t in picked)
        if abbreviates:
            text = self.abbreviated(text)
        abbreviated = bool(self.shorthand.search(text))
        typo = False
        if self.rng.random() < self.settings["with_typo"]:
            slipped = self._typo(text)
            typo, text = slipped != text, slipped
        return Text(
            text,
            tuple(pid for pid, _ in picked),
            ENGLISH,
            abbreviated=abbreviated,
            typo=typo,
            signal=picked[signal][1] if signal is not None else "",
        )

    @functools.cache  # noqa: B019 - one Notes per dataset; its options are the bank's
    def _has_shorthand(self, option: str) -> bool:
        return bool(self.shorthand.search(option))

    def abbreviated(self, text: str) -> str:
        """The text with every expression the team abbreviates abbreviated."""
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


@dataclass(frozen=True)
class _Noted:
    """A Lead as the notes write about it: its facts and the slots it fills."""

    lead: Lead
    facts: frozenset[str]
    values: dict


def _buyer(lead: Lead) -> str:
    return "real_buyer" if lead.real_buyer else "not_real_buyer"
