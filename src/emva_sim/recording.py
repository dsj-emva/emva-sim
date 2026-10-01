"""How the sales team records each Lead's true path in its sales system.

This sits between the true path (process.py) and the export (hubspot.py): which CRM stage changes
the team enters and when. It never changes the true path; what the export shows is decided here,
and hubspot.py shows only what was recorded before the export date.
"""

import calendar
import math
from dataclasses import dataclass, replace
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
    quotes: list[tuple[datetime, float]]  # each itinerary version's Amount and when it was sent


class Recording:
    def __init__(self, p: dict, rng: Random):
        self.p = p
        self.rng = rng
        self.reviews: dict[date, datetime] = {}
        self.stages = p["pipeline"]["stages"]
        self.order = {s["name"]: i for i, s in enumerate(self.stages)}
        self.open = {s["name"] for s in self.stages if "closed" not in s and "after_won" not in s}
        self.lost = next(s["name"] for s in self.stages if s.get("closed") == "lost")

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
        left_out = set()
        if events[-1][0] == self.lost and self.rng.random() < self.p["recording"]["dead_left_open"]:
            left_out.add(len(events) - 1)
        kept = [i for i in range(len(events)) if i not in left_out]
        passed = [i for i in kept[1:-1] if events[i][0] in self.open]
        if passed and self.rng.random() < self.p["recording"]["skips_a_stage"]:
            start = self.rng.randrange(len(passed))
            end = self.rng.randrange(start, len(passed))
            left_out.update(passed[start : end + 1])
        first_stage, created = events[0]
        changes, last = [Change(first_stage, created, created)], created
        for i, (stage, at) in enumerate(events[1:], start=1):
            if i in left_out:
                changes.append(Change(stage, at, None))
                continue
            last = max(self._entered(at), last + MINUTE)
            changes.append(Change(stage, at, last))
        if self.rng.random() < self.p["recording"]["backward_move"]:
            changes = self._move_back(changes)
        no_amount = path.won and self.rng.random() < self.p["recording"]["won_without_amount"]
        return Recorded(changes, [] if no_amount else path.quotes)

    def _move_back(self, changes: list[Change]) -> list[Change]:
        """Move the deal back from one open stage to the stage it was recorded at before.

        If the deal later moves on, it enters that open stage again first; HubSpot overwrites the
        Date entered of both stages entered again. A deal moved back from its last recorded
        stage stays where it was moved back to.
        """
        recorded = [i for i, c in enumerate(changes) if c.recorded_at]
        candidates = [
            (recorded[n - 1], k, recorded[n + 1] if n + 1 < len(recorded) else None)
            for n, k in enumerate(recorded[1:], start=1)
            if changes[k].stage in self.open
        ]
        if not candidates:
            return changes
        before, k, later = self.rng.choice(candidates)
        at = changes[k].recorded_at
        if later is None:
            back = max(self._entered(at), at + MINUTE)
            return [*changes, Change(changes[before].stage, None, back)]
        # The two moves need a minute each before the next change; a later change pushed by
        # them keeps its order.
        until = max(changes[later].recorded_at, at + 3 * MINUTE)
        shift = until - changes[later].recorded_at
        back = at + MINUTE + (until - at - 3 * MINUTE) * self.rng.random()
        again = back + MINUTE + (until - back - 2 * MINUTE) * self.rng.random()
        moves = [Change(changes[before].stage, None, back), Change(changes[k].stage, None, again)]
        rest = [
            replace(c, recorded_at=c.recorded_at + shift) if c.recorded_at else c
            for c in changes[k + 1 :]
        ]
        return [*changes[: k + 1], *moves, *rest]

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
