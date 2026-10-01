"""The Hidden truth of each lead and its true path through the sales process.

A lead's win propensity is its chance of a won Outcome if it is handled normally: base log-odds
plus named effect terms (none planted yet). The base is set so the profile's transition rates hold
on average. The Outcome is drawn from the propensity; a lead that does not win stops at a Stage
drawn from the profile's transition rates, and is moved to Lost when it would have reached the
next one.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random

from emva_sim import draws
from emva_sim.leads import Lead

# The Canonical ladder after Contact attempted; the profile names each transition by its stage.
LADDER_AFTER_CONTACT = ("Engaged", "Qualified", "Proposal", "Won")


@dataclass(frozen=True)
class Attempt:
    at: datetime
    channel: str
    connected: bool


@dataclass(frozen=True)
class TruePath:
    owner: str
    win_propensity: float
    effects: dict[str, float]
    contacted: bool
    reached_stage: str
    won: bool
    stage_times: dict[str, datetime]
    attempts: list[Attempt] = field(default_factory=list)
    quotes: list[tuple[datetime, float]] = field(default_factory=list)
    provisional_hold_at: datetime | None = None
    travelled_at: datetime | None = None
    cancelled_at: datetime | None = None


def _logit(p: float) -> float:
    return math.log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _between(rng: Random, n: int, first: datetime, last: datetime) -> list[datetime]:
    span = (last - first).total_seconds()
    return [first + timedelta(seconds=s) for s in draws.sorted_uniforms(rng, n, 0, span)]


class Process:
    """Draws each lead's true path from the profile's process and handling numbers."""

    def __init__(self, p: dict):
        self.p = p
        handling = p["handling"]
        self.transitions = [p["process"]["transition"][s.lower()] for s in LADDER_AFTER_CONTACT]
        self.base_log_odds = _logit(math.prod(self.transitions))
        self.attempt_median_days = handling["first_attempt_delay_median_hours"] / 24
        self.late_days = handling["late_after_hours"] / 24
        self.late_share = handling["first_attempt_after_24h"]
        self.attempt_sigma = draws.sigma_from_share_above(
            handling["first_attempt_delay_median_hours"],
            handling["late_after_hours"],
            self.late_share,
        )
        reach, failing = 1.0, []
        for rate in self.transitions:
            failing.append(reach * (1 - rate))
            reach *= rate
        self.failing_shares = [share / sum(failing) for share in failing]

    def _effects(self, lead: Lead) -> dict[str, float]:
        return {}

    def _first_attempt_days(self, rng: Random, cycle_days: float) -> float:
        """Days to the first Contact attempt, always before the lead's cycle would end.

        Below late_after_hours it is the lognormal fitted to the median and the late share, so both
        hold; a late attempt is log-uniform between late_after_hours and the end of the cycle.
        """
        if rng.random() < self.late_share and cycle_days > self.late_days:
            return self.late_days * (cycle_days / self.late_days) ** rng.random()
        below = min(self.late_days, cycle_days)
        return draws.lognormal_between(rng, self.attempt_median_days, self.attempt_sigma, 0, below)

    def path(self, rng: Random, lead: Lead) -> TruePath:
        p = self.p
        owner = rng.choice(p["team"]["owners"])
        effects = self._effects(lead)
        propensity = _sigmoid(self.base_log_odds + sum(effects.values()))
        start = lead.submitted_at
        times = {"Submitted": start}
        if rng.random() < p["handling"]["neglected_share"]:
            return TruePath(
                owner=owner,
                win_propensity=propensity,
                effects=effects,
                contacted=False,
                reached_stage="Submitted",
                won=False,
                stage_times=times,
            )

        cycle = lead.cycle_days
        first_attempt = self._first_attempt_days(rng, cycle)
        won = rng.random() < propensity
        stops_before = None if won else rng.choices(LADDER_AFTER_CONTACT, self.failing_shares)[0]

        at = {"Contact attempted": start + timedelta(days=first_attempt)}
        middle = draws.sorted_uniforms(rng, 3, first_attempt, cycle)
        planned = dict(zip(LADDER_AFTER_CONTACT, [*middle, cycle], strict=True))
        reached = "Contact attempted"
        for stage in LADDER_AFTER_CONTACT:
            moment = start + timedelta(days=planned[stage])
            if stage == stops_before:
                at["Lost"] = moment
                break
            at[stage] = moment
            reached = stage
        times.update(at)

        engaged_at = at.get("Engaged")
        attempts = self._attempts(rng, at["Contact attempted"], engaged_at or at["Lost"])
        if engaged_at and rng.random() >= p["handling"]["first_attempt_by_email"]:
            attempts.append(Attempt(engaged_at, "call", True))

        quotes, hold, travelled, cancelled = [], None, None, None
        if "Proposal" in at:
            end = at.get("Won") or at["Lost"]
            quotes = self._quotes(rng, lead, at["Proposal"], end)
            if won or rng.random() < p["process"]["lost_after_provisional_hold"]:
                hold = quotes[-1][0] + (end - quotes[-1][0]) * rng.random()
        if won:
            if rng.random() < p["process"]["won_then_cancelled"]:
                cancelled = at["Won"] + (lead.travel_at - at["Won"]) * rng.random()
            else:
                travelled = lead.travel_at

        return TruePath(
            owner=owner,
            win_propensity=propensity,
            effects=effects,
            contacted=True,
            reached_stage=reached,
            won=won,
            stage_times=times,
            attempts=attempts,
            quotes=quotes,
            provisional_hold_at=hold,
            travelled_at=travelled,
            cancelled_at=cancelled,
        )

    def _attempts(self, rng: Random, first: datetime, until: datetime) -> list[Attempt]:
        handling = self.p["handling"]
        count = 1 + draws.poisson(rng, handling["attempts_before_giving_up"] - 1)
        times = [first, *_between(rng, count - 1, first, until)]
        by_email = handling["first_attempt_by_email"]
        return [Attempt(t, "email" if rng.random() < by_email else "call", False) for t in times]

    def _quotes(
        self, rng: Random, lead: Lead, first: datetime, end: datetime
    ) -> list[tuple[datetime, float]]:
        """Itinerary versions sent; the quote drifts across them and the last is the Deal value."""
        versions = 1 + draws.poisson(rng, self.p["process"]["itinerary_versions_per_won"] - 1)
        if versions == 1:
            return [(first, lead.deal_value)]
        times = [first, *_between(rng, versions - 1, first, end)]
        drift = self.p["deal"]["final_to_first_quote"]
        return [
            (t, lead.deal_value * drift ** (i / (versions - 1) - 1)) for i, t in enumerate(times)
        ]
