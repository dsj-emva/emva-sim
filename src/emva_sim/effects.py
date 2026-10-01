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


def _log(odds_ratio: float) -> float:
    return math.log(odds_ratio)


class Effects:
    def __init__(self, p: dict, history_start: date):
        self.p = p
        self.e = p["effects"]
        months_in = history_start.month - 1 + self.e["price_rise"]["at_month_of_history"] - 1
        self.rise_at = datetime(history_start.year + months_in // 12, months_in % 12 + 1, 1)
        self.seen_at_submission = {
            name for name, effect in self.e.items() if effect["visible"] == ladder.SUBMITTED
        }

    def of_lead(self, lead: Lead) -> dict[str, float]:
        """Every term the lead carries from what it is, whatever its handling."""
        e = self.e
        budget_floor, price_rise = self._budget(lead)
        return {
            "budget_floor": budget_floor,
            "no_budget": 0.0 if lead.states_budget else _log(e["no_budget"]["odds_ratio"]),
            "lead_time_by_season": self._lead_time(lead),
            "date_specificity": self._date_specificity(lead),
            "lead_source": self._lead_source(lead),
            "repeat_client": _log(e["repeat_client"]["odds_ratio"]) if lead.repeat_client else 0.0,
            "message_length": self._message_length(lead),
            "party_size": self._party_size(lead),
            "phone_given": self._phone_given(lead),
            "price_rise": price_rise,
            "text_commitment": (
                _log(e["text_commitment"]["odds_ratio"]) if lead.text_commitment else 0.0
            ),
            "notes_real_buyer": (
                _log(e["notes_real_buyer"]["odds_ratio"]) if lead.real_buyer else 0.0
            ),
        }

    def apparent(self, terms: dict[str, float]) -> float:
        """How good the lead looks at submission: the terms of effects visible then."""
        return sum(value for name, value in terms.items() if name in self.seen_at_submission)

    def response_speed(self, hours_to_first_attempt: float, high_quality: bool) -> float:
        effect = self.e["response_speed_by_quality"]
        if hours_to_first_attempt > effect["within_hours"]:
            return 0.0
        quality = "high_quality_within_1h" if high_quality else "low_quality_within_1h"
        return _log(effect[quality])

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

    def _lead_time(self, lead: Lead) -> float:
        effect = self.e["lead_time_by_season"]
        if lead.dates_given == "not_sure" or lead.months_ahead > effect["over_months"]:
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
