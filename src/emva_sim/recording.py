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

from emva_sim.process import ContactAttempt, TruePath

MINUTE = timedelta(minutes=1)
UNKNOWN = "unknown"


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
    closed_lost_reason: str
    true_loss_reason: str  # Hidden truth: what truly made a lost lead not win
    calls: list[ContactAttempt]  # the call attempts the team logged


class Recording:
    def __init__(self, p: dict, rng: Random):
        self.p = p
        self.rng = rng
        self.reviews: dict[date, datetime] = {}
        self.stages = p["pipeline"]["stages"]
        self.order = {s["name"]: i for i, s in enumerate(self.stages)}
        self.open = {s["name"] for s in self.stages if "closed" not in s and "after_won" not in s}
        self.lost = next(s["name"] for s in self.stages if s.get("closed") == "lost")
        self.reasons = p["loss"]["reasons"]
        self.meanings: dict[str, list[str]] = {}
        for reason in self.reasons["recorded"]:
            self.meanings.setdefault(reason["meaning"], []).append(reason["recorded"])

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

    def lead(self, path: TruePath) -> Recorded:
        """How the team records a genuine Lead's true path, at the profile's [recording] rates.

        A dead lead may be left open at its last stage instead of Lost; a record may skip a run
        of open stages on its way to a later one; each change is entered late or in bulk, never
        before the change recorded ahead of it; a deal may move backward; a won deal may have no
        Amount; a Lost deal's reason may be blank or another than the true one ([loss]).
        """
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
        true_reason = self._true_loss_reason() if events[-1][0] == self.lost else ""
        recorded_lost = any(c.stage == self.lost and c.recorded_at for c in changes)
        reason = self._recorded_loss_reason(true_reason) if recorded_lost else ""
        calls = [a for a in path.attempts if a.channel == "call" and a.logged]
        return Recorded(changes, [] if no_amount else path.quotes, reason, true_reason, calls)

    def not_a_lead(self, submitted_at: datetime) -> Recorded:
        """A duplicate or bot deal: left at its first stage, or moved to Lost.

        No true path lies behind it, so none of its changes has a true time.
        """
        changes = [Change(self.stages[0]["name"], None, submitted_at)]
        reason = ""
        if self.rng.random() < self.p["mess"]["duplicate_or_bot_moved_to_lost"]:
            lost_at = max(self._entered(submitted_at), submitted_at + MINUTE)
            changes.append(Change(self.lost, None, lost_at))
            reason = self._recorded_loss_reason(UNKNOWN)
        return Recorded(changes, [], reason, "", [])

    def _true_loss_reason(self) -> str:
        """What truly made a lost lead not win, drawn from the profile's shares.

        "unknown" takes what the shares leave; shares summing over one are scaled to sum to one.
        """
        shares = {key: self.reasons[key] for key in self.meanings if key != UNKNOWN}
        rest = max(0.0, 1 - sum(shares.values()))
        return self.rng.choices([*shares, UNKNOWN], [*shares.values(), rest])[0]

    def _recorded_loss_reason(self, true_reason: str) -> str:
        """The Closed Lost Reason the team picks: blank, the true one, or another one."""
        loss = self.p["loss"]
        if self.rng.random() < loss["blank_reason"]:
            return ""
        meaning = true_reason
        if self.rng.random() < loss["recorded_differs_from_truth"]:
            meaning = self.rng.choice([m for m in self.meanings if m != true_reason])
        return self.rng.choice(self.meanings[meaning])

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
