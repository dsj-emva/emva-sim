"""The Hidden truth of each lead and its true path through the sales process.

A lead's win propensity is its chance of a won Outcome once contacted: the base log-odds plus one
term per planted effect (emva_sim.effects), response speed included once the first Contact attempt
is drawn. The base is solved so that contacted leads' propensities average the profile's win rate,
and so its transition rates hold on average. The Outcome is drawn from the propensity; a lead that
does not win stops at a Stage drawn from the profile's transition rates, and is moved to Lost when
it would have reached the next one. A Neglected lead keeps its propensity and is never won.
"""

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from random import Random

from emva_sim import draws, ladder
from emva_sim.effects import RESPONSE_SPEED, Effects
from emva_sim.leads import Lead
from emva_sim.logistic import logit, sigmoid


@dataclass(frozen=True)
class ContactAttempt:
    at: datetime
    channel: str
    connected: bool
    logged: bool


@dataclass(frozen=True)
class TruePath:
    owner: str
    base_log_odds: float
    terms: dict[str, float]
    high_quality: bool
    neglected_lead: bool
    reached_stage: str
    won: bool
    stage_times: dict[str, datetime]
    attempts: list[ContactAttempt] = field(default_factory=list)
    quotes: list[tuple[datetime, float]] = field(default_factory=list)
    provisional_hold_at: datetime | None = None
    travelled_at: datetime | None = None
    cancelled_at: datetime | None = None

    @property
    def win_propensity(self) -> float:
        return win_propensity(self.base_log_odds, self.terms)


def win_propensity(base_log_odds: float, terms: dict[str, float]) -> float:
    """A lead's chance of a won Outcome once contacted: the base plus its terms, on the log-odds."""
    return sigmoid(base_log_odds + sum(terms.values()))


def _base_log_odds(terms: list[float], target: float) -> float:
    """The base whose propensities, with these summed terms, average target (Newton's method)."""
    counted = Counter(terms)
    n = sum(counted.values())
    base = logit(target)
    for _ in range(100):
        chances = {t: sigmoid(base + t) for t in counted}
        mean = sum(counted[t] * c for t, c in chances.items()) / n
        slope = sum(counted[t] * c * (1 - c) for t, c in chances.items()) / n
        step = (mean - target) / slope
        base -= step
        if abs(step) < 1e-12:
            return base
    raise ArithmeticError("the base log-odds did not converge")


def _mid_ranks(values: list[float]) -> list[float]:
    """Each value's place among them from 0 (lowest) to 1 (highest), ties sharing the middle."""
    counted = Counter(values)
    below, place = 0, {}
    for value in sorted(counted):
        place[value] = (below + counted[value] / 2) / len(values)
        below += counted[value]
    return [place[v] for v in values]


def _top(rng: Random, values: list[float], share: float) -> list[bool]:
    """Whether each value is among the top share of them, ties at the edge broken at random."""
    tie_breaks = [rng.random() for _ in values]
    ranked = sorted(range(len(values)), key=lambda i: (values[i], tie_breaks[i]), reverse=True)
    top = set(ranked[: round(share * len(values))])
    return [i in top for i in range(len(values))]


@dataclass(frozen=True)
class _Start:
    owner: str
    neglected_lead: bool
    first_attempt_days: float | None


def _between(rng: Random, n: int, first: datetime, last: datetime) -> list[datetime]:
    span = (last - first).total_seconds()
    return [first + timedelta(seconds=s) for s in draws.sorted_uniforms(rng, n, 0, span)]


class Process:
    """Draws each lead's true path from the profile's process and handling numbers."""

    def __init__(self, p: dict, history_start: date):
        self.p = p
        handling = p["handling"]
        self.effects = Effects(p, history_start)
        self.transitions = [p["process"]["transition"][s.lower()] for s in ladder.AFTER_CONTACT]
        self.win_rate = math.prod(self.transitions)
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

    def _first_attempt_days(self, rng: Random, cycle_days: float) -> float:
        """Days to the first Contact attempt, always before the lead's cycle would end.

        Below late_after_hours it is the lognormal fitted to the median and the late share, so both
        hold; a late attempt is log-uniform between late_after_hours and the end of the cycle.
        """
        if rng.random() < self.late_share and cycle_days > self.late_days:
            return self.late_days * (cycle_days / self.late_days) ** rng.random()
        below = min(self.late_days, cycle_days)
        return draws.lognormal_between(rng, self.attempt_median_days, self.attempt_sigma, 0, below)

    def paths(self, rng: Random, leads: list[Lead]) -> list[TruePath]:
        """Every lead's true path. Quality and neglect are read against the other leads."""
        terms = [self.effects.of_lead(lead) for lead in leads]
        speed = self.p["effects"][RESPONSE_SPEED]
        high = _top(rng, [sum(t.values()) for t in terms], speed["high_quality_top_share"])
        looks = _mid_ranks([self.effects.apparent(t) for t in terms])
        starts = [self._start(rng, lead, place) for lead, place in zip(leads, looks, strict=True)]
        terms = [
            self.effects.with_response_speed(
                t,
                0.0
                if start.first_attempt_days is None
                else self.effects.response_speed(24 * start.first_attempt_days, quality),
            )
            for t, start, quality in zip(terms, starts, high, strict=True)
        ]
        contacted = [
            sum(t.values()) for t, s in zip(terms, starts, strict=True) if not s.neglected_lead
        ]
        base = _base_log_odds(contacted, self.win_rate) if contacted else logit(self.win_rate)
        return [self._path(rng, *row, base) for row in zip(leads, starts, terms, high, strict=True)]

    def _start(self, rng: Random, lead: Lead, looks: float) -> _Start:
        """Owner, neglect and the first Contact attempt: the advertiser's handling of the lead.

        A share of the neglect decision (neglect_follows_apparent_quality) neglects a lead with a
        chance falling linearly from twice neglected_share for the worst-looking lead to zero for
        the best (looks is its place among the leads, from 0 to 1, by the terms visible at
        submission); the rest neglects any lead at neglected_share. A neglected lead keeps its
        propensity.
        """
        handling = self.p["handling"]
        owner = rng.choice(self.p["team"]["owners"])
        share = handling["neglected_share"]
        if rng.random() < handling["neglect_follows_apparent_quality"]:
            share = min(1.0, 2 * share * (1 - looks))
        if rng.random() < share:
            return _Start(owner, True, None)
        return _Start(owner, False, self._first_attempt_days(rng, lead.cycle_days))

    def _path(
        self,
        rng: Random,
        lead: Lead,
        start: _Start,
        terms: dict[str, float],
        high_quality: bool,
        base: float,
    ) -> TruePath:
        p = self.p
        owner = start.owner
        hidden = {"base_log_odds": base, "terms": terms, "high_quality": high_quality}
        start_at = lead.submitted_at
        times = {ladder.SUBMITTED: start_at}
        if start.neglected_lead:
            return TruePath(
                owner=owner,
                **hidden,
                neglected_lead=True,
                reached_stage=ladder.SUBMITTED,
                won=False,
                stage_times=times,
            )

        cycle = lead.cycle_days
        first_attempt = start.first_attempt_days
        won = rng.random() < win_propensity(base, terms)
        stops_before = None if won else rng.choices(ladder.AFTER_CONTACT, self.failing_shares)[0]

        at = {ladder.CONTACT_ATTEMPTED: start_at + timedelta(days=first_attempt)}
        middle = draws.sorted_uniforms(rng, 3, first_attempt, cycle)
        planned = dict(zip(ladder.AFTER_CONTACT, [*middle, cycle], strict=True))
        reached = ladder.CONTACT_ATTEMPTED
        for stage in ladder.AFTER_CONTACT:
            moment = start_at + timedelta(days=planned[stage])
            if stage == stops_before:
                at[ladder.LOST] = moment
                break
            at[stage] = moment
            reached = stage
        times.update(at)

        engaged_at = at.get(ladder.ENGAGED)
        attempts = self._attempts(rng, at[ladder.CONTACT_ATTEMPTED], engaged_at or at[ladder.LOST])
        if engaged_at and rng.random() >= p["handling"]["attempt_by_email"]:
            attempts.append(ContactAttempt(engaged_at, "call", True, self._logged(rng)))

        quotes, hold, travelled, cancelled = [], None, None, None
        if ladder.PROPOSAL in at:
            end = at.get(ladder.WON) or at[ladder.LOST]
            quotes = self._quotes(rng, lead, at[ladder.PROPOSAL], end)
            if won or rng.random() < p["process"]["lost_after_provisional_hold"]:
                hold = quotes[-1][0] + (end - quotes[-1][0]) * rng.random()
        if won:
            if rng.random() < p["process"]["won_then_cancelled"]:
                cancelled = at[ladder.WON] + (lead.travel_at - at[ladder.WON]) * rng.random()
            else:
                travelled = lead.travel_at

        return TruePath(
            owner=owner,
            **hidden,
            neglected_lead=False,
            reached_stage=reached,
            won=won,
            stage_times=times,
            attempts=attempts,
            quotes=quotes,
            provisional_hold_at=hold,
            travelled_at=travelled,
            cancelled_at=cancelled,
        )

    def _attempts(self, rng: Random, first: datetime, until: datetime) -> list[ContactAttempt]:
        handling = self.p["handling"]
        count = 1 + draws.poisson(rng, handling["attempts_before_giving_up"] - 1)
        times = [first, *_between(rng, count - 1, first, until)]
        by_email = handling["attempt_by_email"]
        return [
            ContactAttempt(
                t, "email" if rng.random() < by_email else "call", False, self._logged(rng)
            )
            for t in times
        ]

    def _logged(self, rng: Random) -> bool:
        """Whether the sales team logs this Contact attempt in its sales system."""
        return rng.random() < self.p["handling"]["attempts_logged"]

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
