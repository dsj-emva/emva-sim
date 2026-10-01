"""The planted effects: each a named term on a lead's win log-odds, in the profile's own form.

A term is the log of the profile's odds ratio for the lead's group at the resolved setting, and zero
in the effect's reference group. The proxy trap has no term: it moves the lead draws and nothing
else. Response speed is the advertiser's handling, known only once the first Contact attempt is
drawn, so it has a method of its own.
"""

import math
from datetime import date, datetime

from emva_sim import form, ladder
from emva_sim.leads import Lead

SPEED_LIFT_BETWEEN = "linear in log hours"
RESPONSE_SPEED = "response_speed_by_quality"
# The form of an effect that has no term of its own (the proxy trap).
NO_TERM = "confounded"


def term_names(p: dict) -> list[str]:
    """The planted effects that carry a term, in the profile's order."""
    return [name for name, effect in p["effects"].items() if effect["form"] != NO_TERM]


def _log(odds_ratio: float) -> float:
    return math.log(odds_ratio)


class Effects:
    def __init__(self, p: dict, history_start: date):
        self.p = p
        self.e = p["effects"]
        months_in = history_start.month - 1 + self.e["price_rise"]["at_month_of_history"] - 1
        self.rise_at = datetime(history_start.year + months_in // 12, months_in % 12 + 1, 1)
        if self.e[RESPONSE_SPEED]["lift_between"] != SPEED_LIFT_BETWEEN:
            raise ValueError(f"response speed's lift between must be {SPEED_LIFT_BETWEEN!r}")
        self.names = term_names(p)
        self._terms = {
            "budget_floor": lambda lead: self._budget(lead)[0],
            "no_budget": self._no_budget,
            "lead_time_by_season": self._lead_time,
            "date_specificity": self._date_specificity,
            "lead_source": self._lead_source,
            "repeat_client": self._repeat_client,
            "message_length": self._message_length,
            "party_size": self._party_size,
            "phone_given": self._phone_given,
            "price_rise": lambda lead: self._budget(lead)[1],
            "text_commitment": self._text_commitment,
            "notes_real_buyer": self._notes_real_buyer,
        }
        unknown = set(self.names) - set(self._terms) - {RESPONSE_SPEED}
        if unknown:
            raise ValueError(f"the generator cannot compute the effects {sorted(unknown)}")
        self.seen_at_submission = {
            name for name, effect in self.e.items() if effect["visible"] == ladder.SUBMITTED
        }

    def of_lead(self, lead: Lead) -> dict[str, float]:
        """Every term the lead carries from what it is, whatever its handling, in profile order."""
        return {name: self._terms[name](lead) for name in self.names if name != RESPONSE_SPEED}

    def with_response_speed(self, terms: dict[str, float], speed: float) -> dict[str, float]:
        """The lead's terms with response speed's added, in profile order."""
        return {name: speed if name == RESPONSE_SPEED else terms[name] for name in self.names}

    def apparent(self, terms: dict[str, float]) -> float:
        """How good the lead looks at submission: the terms of effects visible then."""
        return sum(value for name, value in terms.items() if name in self.seen_at_submission)

    def response_speed(self, hours_to_first_attempt: float, high_quality: bool) -> float:
        """The full lift within within_hours, none from no_lift_from_hours, linear in log hours
        between (the profile's lift_between)."""
        effect = self.e[RESPONSE_SPEED]
        quick, slow = effect["within_hours"], effect["no_lift_from_hours"]
        quality = "high_quality_within_1h" if high_quality else "low_quality_within_1h"
        hours = min(max(hours_to_first_attempt, quick), slow)
        return _log(effect[quality]) * math.log(slow / hours) / math.log(slow / quick)

    def _budget(self, lead: Lead) -> tuple[float, float]:
        """The budget-floor and price-rise terms of a stated budget.

        After the rise the floor is higher, so a budget it puts below the floor takes the floor's
        term; one at or above the new floor but near the old one takes the rise's term.
        """
        if not lead.states_budget:
            return 0.0, 0.0
        floor, rise = self.e["budget_floor"], self.e["price_rise"]
        price = self.p["deal"]["price_per_person_per_night"][lead.style]
        old_floor = floor["floor_share_of_style_price"] * price
        after = lead.submitted_at >= self.rise_at
        current = old_floor * (1 + rise["floor_rise"]) if after else old_floor
        budget = lead.budget_per_person_per_night
        if budget < floor["below_half_under"] * current:
            penalty = _log(floor["below_half"])
        elif budget < current:
            penalty = _log(floor["half_to_floor"])
        else:
            penalty = 0.0
        if lead.repeat_client:
            penalty *= self.e["repeat_client"]["floor_penalty_kept"]
        near = after and current <= budget < rise["near_floor_under"] * old_floor
        return penalty, _log(rise["near_floor_after"]) if near else 0.0

    def _flag(self, effect: str, flag: bool) -> float:
        return _log(self.e[effect]["odds_ratio"]) if flag else 0.0

    def _no_budget(self, lead: Lead) -> float:
        return self._flag("no_budget", not lead.states_budget)

    def _repeat_client(self, lead: Lead) -> float:
        return self._flag("repeat_client", lead.repeat_client)

    def _text_commitment(self, lead: Lead) -> float:
        return self._flag("text_commitment", lead.text_commitment)

    def _notes_real_buyer(self, lead: Lead) -> float:
        return self._flag("notes_real_buyer", lead.real_buyer)

    def _lead_time(self, lead: Lead) -> float:
        effect = self.e["lead_time_by_season"]
        if lead.dates_given in ("year", "not_sure") or lead.months_ahead > effect["over_months"]:
            return _log(effect["over_18_months_or_unsure"])
        if lead.months_ahead < effect["under_months"]:
            peak = lead.travel_at.month in self.p["season"]["peak_months"]
            return _log(effect["peak_under_4_months" if peak else "off_peak_under_4_months"])
        return 0.0

    def _date_specificity(self, lead: Lead) -> float:
        effect = self.e["date_specificity"]
        match lead.dates_given:
            case "exact":
                return 0.0
            case "month":
                return _log(effect["month_only"])
        return _log(effect["no_dates"])

    def _lead_source(self, lead: Lead) -> float:
        if lead.traffic_source == self.p["volume"]["traffic_source"]["reference"]:
            return 0.0
        return _log(self.e["lead_source"][lead.traffic_source])

    def _message_length(self, lead: Lead) -> float:
        effect, shape = self.e["message_length"], self.p["form"]["message"]["shape"]
        if lead.message_words < effect["under_words"]:
            return _log(effect["under_15_words"])
        dreamer = (
            lead.message_words > shape["dreamer_over_words"]
            and len(lead.destinations) > shape["dreamer_over_countries"]
            and not lead.states_budget
        )
        return _log(effect["dreamer"]) if dreamer else 0.0

    def _party_size(self, lead: Lead) -> float:
        effect = self.e["party_size"]
        return _log(effect["over_6"]) if lead.party_size > effect["over_travellers"] else 0.0

    def _phone_given(self, lead: Lead) -> float:
        if not lead.gives_phone or form.field(self.p, "phone")["required"]:
            return 0.0
        return _log(self.e["phone_given"]["odds_ratio_when_optional"])
