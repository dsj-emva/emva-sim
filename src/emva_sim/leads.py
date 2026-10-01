"""Leads as they arrive: when each is submitted, the trip it wants, and its answers to the form."""

import calendar
import math
import re
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from random import Random

from emva_sim import draws, people

DAYS_PER_MONTH = 365.25 / 12


@dataclass(frozen=True)
class Lead:
    submitted_at: datetime
    market_group: str
    country: str
    traffic_source: str
    repeat_client: bool
    style: str
    nights: int
    adults: int
    children: int
    price_per_person_per_night: float
    cycle_days: float
    travel_at: datetime
    answers: dict[str, str] = field(default_factory=dict)

    @property
    def deal_value(self) -> float:
        return self.price_per_person_per_night * self.nights * (self.adults + self.children)


def _span(year: int, month: int, start: date, end: date) -> tuple[date, date]:
    first = max(date(year, month, 1), start)
    return first, min(date(year, month, calendar.monthrange(year, month)[1]), end)


def _months(start: date, end: date) -> list[tuple[int, int, float]]:
    """Each calendar month the history touches, with the share of that month it covers."""
    months, year, month = [], start.year, start.month
    while (year, month) <= (end.year, end.month):
        first, last = _span(year, month, start, end)
        months.append(
            (year, month, ((last - first).days + 1) / calendar.monthrange(year, month)[1])
        )
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def _month_weights(p: dict, group: str) -> dict[int, float]:
    seasonality = p["volume"]["seasonality"]
    weights = dict.fromkeys(range(1, 13), 1.0)
    for name, weight in seasonality[seasonality["markets"][group.lower()]].items():
        for month in seasonality["months"][name]:
            weights[month] = weight
    return weights


def _submitted_at(rng: Random, year: int, month: int, start: date, end: date) -> datetime:
    first, last = _span(year, month, start, end)
    minutes = ((last - first).days + 1) * 24 * 60
    return datetime.combine(first, datetime.min.time()) + timedelta(minutes=rng.randrange(minutes))


def _pick(rng: Random, shares: dict[str, float], rest: str) -> str:
    u = rng.random()
    for name, share in shares.items():
        if u < share:
            return name
        u -= share
    return rest


def _bounds(option: str) -> tuple[float, float] | None:
    numbers = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", option)]
    if option.startswith("Under"):
        return -math.inf, numbers[0]
    if option.endswith("+"):
        return numbers[0], math.inf
    if len(numbers) == 2:
        return numbers[0], numbers[1]
    return None


def band(value: float, options: list[str]) -> str:
    """The first option whose band holds value: "Under X" (below X), "A - B" (inclusive) or "N+"."""
    for option in options:
        bounds = _bounds(option)
        if bounds is None:
            continue
        low, high = bounds
        if (value < high) if math.isinf(low) else (low <= value <= high):
            return option
    raise ValueError(f"{value} is in no band of {options}")


def _key(label: str) -> str:
    return label.lower().replace("-", "_")


def _field(p: dict, role: str) -> dict:
    return next(f for f in p["form"]["fields"] if f["role"] == role)


def _unsure(options: list[str]) -> str:
    return next(option for option in options if option.startswith("Not sure"))


def _travel_answer(rng: Random, p: dict, travel: date) -> str:
    answers = p["form"]["answers"]
    if rng.random() < answers["states_exact_dates"]:
        return travel.isoformat()
    if rng.random() < answers["month_when_no_exact_dates"]:
        return f"{calendar.month_name[travel.month]} {travel.year}"
    if rng.random() < answers["year_when_no_month"]:
        return str(travel.year)
    return "Not sure"


def _destinations(rng: Random, p: dict, options: list[str]) -> str:
    count = 1 + draws.poisson(rng, p["form"]["answers"]["countries_named"] - 1)
    chosen = rng.sample(options, min(count, len(options)))
    unsure = _unsure(options)
    return unsure if unsure in chosen else ";".join(o for o in options if o in chosen)


def _heard_about(rng: Random, p: dict, lead: Lead) -> str:
    source = p["volume"]["traffic_source"]
    if rng.random() >= p["form"]["answers"]["answers_how_heard"]:
        return ""
    if lead.repeat_client:
        return source["heard_as_repeat_client"]
    return rng.choice(source["heard_as"][lead.traffic_source])


def _answer(rng: Random, p: dict, lead: Lead, person: people.Person, form_field: dict) -> str:
    answers = p["form"]["answers"]
    options = form_field.get("options", [])
    match form_field["role"]:
        case "title":
            return person.title
        case "first_name":
            return person.first_name
        case "last_name":
            return person.last_name
        case "email":
            return person.email
        case "phone":
            return person.phone if rng.random() < answers["gives_phone_when_optional"] else ""
        case "country":
            return lead.country
        case "destinations":
            return _destinations(rng, p, options)
        case "travel_date":
            return _travel_answer(rng, p, lead.travel_at.date())
        case "dates_flexible":
            return rng.choice(options)
        case "newsletter":
            return rng.choice(["Yes", "No"])
        case "nights":
            return band(lead.nights, options)
        case "adults":
            return str(lead.adults)
        case "children":
            return str(lead.children) if lead.children else ""
        case "children_ages":
            return ", ".join(
                str(age) for age in sorted(rng.randrange(18) for _ in range(lead.children))
            )
        case "style":
            return lead.style
        case "budget_per_person":
            stated = rng.random() < answers["states_budget"]
            return band(lead.price_per_person_per_night * lead.nights, options) if stated else ""
        case "travelled_before":
            return "Yes" if lead.repeat_client else "No"
        case "heard_about":
            return _heard_about(rng, p, lead)
        case "message":
            return ""
    raise ValueError(f"the generator does not know the form role {form_field['role']!r}")


def _style(rng: Random, p: dict) -> str:
    options = _field(p, "style")["options"]
    styles = [o for o in options if o != _unsure(options)]
    mix = p["deal"]["style_mix"]
    rest = next(s for s in styles if _key(s) not in mix)
    chosen = _pick(rng, mix, _key(rest))
    return next(s for s in styles if _key(s) == chosen)


def _party(rng: Random, p: dict) -> tuple[int, int]:
    size = p["form"]["party_size"]
    match _pick(rng, p["form"]["party_mix"], "solo"):
        case "couple":
            return 2, 0
        case "family":
            return 2, 1 + draws.poisson(rng, size["family_children"] - 1)
        case "friends":
            return 2 + draws.poisson(rng, size["friends_adults"] - 2), 0
    return 1, 0


def _lead(rng: Random, p: dict, submitted_at: datetime, group: str) -> Lead:
    deal, process, source = p["deal"], p["process"], p["volume"]["traffic_source"]
    country = rng.choice(p["effects"]["proxy_trap_country"][f"group_{group.lower()}_countries"])
    others = {k: source[k] for k in source["labels"] if k != source["reference"]}
    traffic_source = _pick(rng, others, source["reference"])
    repeat_client = rng.random() < p["effects"]["repeat_client"]["share_of_leads"]
    adults, children = _party(rng, p)
    style = _style(rng, p)
    nights = max(1, round(draws.lognormal(rng, deal["nights"], deal["nights_sigma"])))
    cycle_days = draws.lognormal(rng, process["days_to_won_median"], process["days_to_won_sigma"])
    lead_time_days = DAYS_PER_MONTH * draws.lognormal(
        rng, process["booking_lead_time_months"], process["booking_lead_time_sigma"]
    )
    travel_at = submitted_at + timedelta(days=cycle_days + lead_time_days)
    price = deal["price_per_person_per_night"][_key(style)]
    if travel_at.month in p["effects"]["lead_time_by_season"]["peak_months"]:
        price *= deal["peak_to_low_season_rate"]
    lead = Lead(
        submitted_at=submitted_at,
        market_group=group,
        country=country,
        traffic_source=traffic_source,
        repeat_client=repeat_client,
        style=style,
        nights=nights,
        adults=adults,
        children=children,
        price_per_person_per_night=price,
        cycle_days=cycle_days,
        travel_at=travel_at,
    )
    person = people.draw(rng, country)
    answers = {f["label"]: _answer(rng, p, lead, person, f) for f in p["form"]["fields"]}
    return replace(lead, answers=answers)


def draw_leads(rng: Random, p: dict, start: date, end: date) -> list[Lead]:
    """Every lead submitted from start to end (inclusive), at the profile's volume and season."""
    months = _months(start, end)
    weights = {group: _month_weights(p, group) for group in ("A", "B")}
    count = round(p["volume"]["leads_per_month"] * sum(share for _, _, share in months))
    arrivals = []
    for _ in range(count):
        group = "A" if rng.random() < p["effects"]["proxy_trap_country"]["group_a_share"] else "B"
        chances = [weights[group][m] * share for _, m, share in months]
        year, month, _ = rng.choices(months, chances)[0]
        arrivals.append((_submitted_at(rng, year, month, start, end), group))
    return [_lead(rng, p, at, group) for at, group in sorted(arrivals)]
