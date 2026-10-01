"""How the sales team records each Lead's true path in its sales system.

This sits between the true path (process.py) and the export (hubspot.py): which CRM stage changes
the team enters and when. It never changes the true path; what the export shows is decided here,
and hubspot.py shows only what was recorded before the export date.
"""

import calendar
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from random import Random

from emva_sim.leads import Lead
from emva_sim.process import TruePath

MINUTE = timedelta(minutes=1)


@dataclass(frozen=True)
class Change:
    """One CRM stage change: when it truly happened and when the team recorded it.

    true_at is None for a change with no true event behind it; recorded_at is None for a true
    event the team never recorded.
    """

    stage: str
    true_at: datetime | None
    recorded_at: datetime | None


@dataclass(frozen=True)
class Recorded:
    changes: list[Change]


class Recording:
    def __init__(self, p: dict, rng: Random):
        self.p = p
        self.rng = rng
        self.reviews: dict[date, datetime] = {}
        self.stages = p["pipeline"]["stages"]
        self.order = {s["name"]: i for i, s in enumerate(self.stages)}

    def true_events(self, path: TruePath) -> list[tuple[str, datetime]]:
        """Each CRM stage the deal truly entered and when, in the order it entered them."""
        events = []
        for stage in self.stages:
            if stage.get("milestone"):
                moment = path.provisional_hold_at
            elif stage.get("after_won") == "travelled":
                moment = path.travelled_at
            elif stage.get("after_won") == "cancelled":
                moment = path.cancelled_at
            else:
                moment = path.stage_times.get(stage["ladder"])
            if moment is not None:
                events.append((stage["name"], moment))
        return sorted(events, key=lambda event: (event[1], self.order[event[0]]))

    def lead(self, lead: Lead, path: TruePath) -> Recorded:
        events = self.true_events(path)
        first_stage, created = events[0]
        changes = [Change(first_stage, created, created)]
        for stage, at in events[1:]:
            entered = max(self._entered(at), changes[-1].recorded_at + MINUTE)
            changes.append(Change(stage, at, entered))
        return Recorded(changes)

    def _entered(self, at: datetime) -> datetime:
        """When the team records a change that truly happened at this moment.

        The deal's creation at its first stage is the form's; every later change is entered by
        hand: in bulk at the next weekly pipeline review, or an exponential lag after the event
        with the profile's median.
        """
        if self.rng.random() < self.p["recording"]["bulk_update_share"]:
            return self._review_after(at)
        median = self.p["recording"]["lag_days_median"]
        lag = self.rng.expovariate(math.log(2) / median) if median else 0.0
        return at + timedelta(days=lag)

    def _review_after(self, at: datetime) -> datetime:
        """The first weekly pipeline review after this moment: one timestamp for its bulk edit."""
        review = self.p["recording"]["bulk_review"]
        ahead = (list(calendar.day_name).index(review["weekday"]) - at.weekday()) % 7
        day = at.date() + timedelta(days=ahead)
        while (moment := self._review_on(day)) <= at:
            day += timedelta(days=7)
        return moment

    def _review_on(self, day: date) -> datetime:
        if day not in self.reviews:
            review = self.p["recording"]["bulk_review"]
            minutes = self.rng.randrange((review["to_hour"] - review["from_hour"]) * 60)
            start = datetime.combine(day, time(review["from_hour"]))
            self.reviews[day] = start + timedelta(minutes=minutes)
        return self.reviews[day]
