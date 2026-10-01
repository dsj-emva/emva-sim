"""Exports in the shape HubSpot writes them.

As docs/research/planned-hospitality/sales-steps-and-exports.md §3 records: every field
double-quoted, header = the property's label, datetimes "YYYY-MM-DD HH:MM", numbers as decimals,
multi-value cells joined with ";", owners as names. Only what the sales team has recorded before
the export date appears.
"""

import csv
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from random import Random

from emva_sim import form, months
from emva_sim.intake import Submission
from emva_sim.recording import Change, Recorded, closed_stage

UNCONNECTED_CALL_OUTCOMES = ["No answer", "Left voicemail", "Busy"]
DEAL_RECORD_IDS_FROM = 10_000_000_000
CONTACT_RECORD_IDS_FROM = 100_000
CALL_RECORD_IDS_FROM = 30_000_000_000


def record_ids(rng: Random, count: int, after: int) -> list[int]:
    """Increasing Record IDs after a starting number, with gaps as HubSpot leaves them."""
    ids, current = [], after
    for _ in range(count):
        current += rng.randint(1, 99)
        ids.append(current)
    return ids


@dataclass(frozen=True)
class Record:
    """One deal and its contact, as the sales system holds them."""

    deal_id: int
    contact_id: int
    owner: str
    submission: Submission
    recorded: Recorded


def stamp(moment: datetime | None) -> str:
    return moment.strftime("%Y-%m-%d %H:%M") if moment else ""


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def file_name(view: str, export_date: date) -> str:
    return f"hubspot-crm-exports-{slug(view)}-{export_date.isoformat()}.csv"


def date_entered(stage: str, pipeline: str) -> str:
    return f'Date entered "{stage} ({pipeline})"'


def _write(path: Path, header: list[str], rows: Iterable[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)


def _decimal(value: float) -> str:
    return str(float(round(value, 2)))


class Export:
    def __init__(self, p: dict, records: list[Record], export_date: date):
        self.p = p
        self.records = records
        self.export_date = export_date
        self.export_at = datetime.combine(export_date, datetime.min.time())
        self.pipeline = p["pipeline"]["name"]
        self.stages = p["pipeline"]["stages"]
        self.lost = closed_stage(p, "lost")
        self.won = closed_stage(p, "won")
        self.fields = p["form"]["fields"]

    def write(self, folder: Path, rng: Random) -> None:
        deals = (self._deals_header(), [self._deal_row(r) for r in self.records])
        contacts = (self._contacts_header(), [self._contact_row(r) for r in self.records])
        calls = (self._calls_header(), self._call_rows(rng))
        for variant in self.p["exports"]["variants"]:
            target = folder / slug(variant["name"])
            _write(target / file_name(self.pipeline, self.export_date), *deals)
            _write(target / file_name("All contacts", self.export_date), *contacts)
            if variant["calls"]:
                _write(target / file_name("All calls", self.export_date), *calls)

    def _recorded(self, moment: datetime | None) -> datetime | None:
        return moment if moment is not None and moment < self.export_at else None

    def stage_times(self, r: Record) -> dict[str, datetime]:
        """The latest recorded entry of each CRM stage, for the changes recorded before the export.

        HubSpot overwrites a stage's Date entered when a deal enters it again.
        """
        return {c.stage: c.recorded_at for c in self._visible(r)}

    def _visible(self, r: Record) -> list[Change]:
        recorded = [c for c in r.recorded.changes if self._recorded(c.recorded_at)]
        return sorted(recorded, key=lambda c: c.recorded_at)

    def _answer(self, s: Submission, form_field: dict) -> str:
        value = s.answers[form_field["label"]]
        return _decimal(float(value)) if form_field["kind"] == "number" and value else value

    def _deal_name(self, s: Submission) -> str:
        destination = form.answer(self.p, s.answers, "destinations").split(";")[0]
        place = (
            "" if destination in ("", form.unsure(self.p, "destinations")) else f" {destination}"
        )
        return f"{form.answer(self.p, s.answers, 'last_name')} –{place} {s.travel_month}"

    def _contact_name(self, s: Submission) -> str:
        first = form.answer(self.p, s.answers, "first_name")
        return f"{first} {form.answer(self.p, s.answers, 'last_name')}"

    def _closed(self, times: dict[str, datetime]) -> datetime | None:
        for stage in self.stages:
            if stage.get("closed") and stage["name"] in times:
                return times[stage["name"]]
        return None

    def _deals_header(self) -> list[str]:
        return [
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
            *(date_entered(s["name"], self.pipeline) for s in self.stages),
            *self.p["exports"]["deal_properties"],
            "Associated Contact",
            "Associated Contact IDs",
        ]

    def _deal_row(self, r: Record) -> list[str]:
        s = r.submission
        times = self.stage_times(r)
        current = self._visible(r)[-1].stage
        quotes = [amount for at, amount in r.recorded.quotes if self._recorded(at)]
        created = s.submitted_at
        month_end = months.last_day(created.year, created.month)
        close = self._closed(times) or datetime.combine(month_end, datetime.min.time())
        by_label = {f["label"]: f for f in self.fields}
        return [
            str(r.deal_id),
            self._deal_name(s),
            self.pipeline,
            current,
            _decimal(quotes[-1]) if quotes else "",
            stamp(close),
            stamp(created),
            r.owner,
            "Existing Business" if s.repeat_client else "New Business",
            r.recorded.closed_lost_reason if current == self.lost else "",
            self.p["volume"]["traffic_source"]["labels"][s.traffic_source],
            "Forms",
            *(stamp(times.get(stage["name"])) for stage in self.stages),
            *(self._answer(s, by_label[label]) for label in self.p["exports"]["deal_properties"]),
            self._contact_name(s),
            str(r.contact_id),
        ]

    def _contacts_header(self) -> list[str]:
        standard = self.p["exports"]["contact_properties"]
        return [
            "Record ID",
            *(standard[f["label"]] for f in self.fields if f["label"] in standard),
            "Lifecycle Stage",
            "Contact owner",
            "Create Date",
            "Original Traffic Source",
            *(f["label"] for f in self.fields if f["label"] not in standard),
            "Associated Deal",
            "Associated Deal IDs",
        ]

    def _contact_row(self, r: Record) -> list[str]:
        s = r.submission
        standard = self.p["exports"]["contact_properties"]

        return [
            str(r.contact_id),
            *(self._answer(s, f) for f in self.fields if f["label"] in standard),
            "Customer" if self.won in self.stage_times(r) else "Opportunity",
            r.owner,
            stamp(s.submitted_at),
            self.p["volume"]["traffic_source"]["labels"][s.traffic_source],
            *(self._answer(s, f) for f in self.fields if f["label"] not in standard),
            self._deal_name(s),
            str(r.deal_id),
        ]

    def _calls_header(self) -> list[str]:
        return [
            "Record ID",
            "Activity date",
            "Call title",
            "Call notes",
            "Call outcome",
            "Call status",
            "Call direction",
            "Associated Contact",
            "Associated Contact IDs",
            "Associated Deal",
            "Associated Deal IDs",
        ]

    def _call_rows(self, rng: Random) -> list[list[str]]:
        calls = sorted(
            (attempt.at, r.deal_id, attempt)
            for r in self.records
            for attempt in r.recorded.calls
            if self._recorded(attempt.at)
        )
        by_deal = {r.deal_id: r for r in self.records}
        rows = []
        call_ids = record_ids(rng, len(calls), CALL_RECORD_IDS_FROM)
        for call_id, (at, deal_id, attempt) in zip(call_ids, calls, strict=True):
            r = by_deal[deal_id]
            outcome = "Connected" if attempt.connected else rng.choice(UNCONNECTED_CALL_OUTCOMES)
            rows.append(
                [
                    str(call_id),
                    stamp(at),
                    f"Call with {self._contact_name(r.submission)}",
                    "",
                    outcome,
                    "Completed",
                    "Outbound",
                    self._contact_name(r.submission),
                    str(r.contact_id),
                    self._deal_name(r.submission),
                    str(deal_id),
                ]
            )
        return rows
