"""Leads as they arrive: when each is submitted, the trip it wants, and its answers to the form."""

import calendar
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from random import Random

from emva_sim import draws, form, months, people

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
    budget_per_person_per_night: float
    cycle_days: float
    travel_at: datetime
    answers: dict[str, str] = field(default_factory=dict)

    @property
    def deal_value(self) -> float:
        return self.price_per_person_per_night * self.nights * (self.adults + self.children)


def _month_weights(p: dict, group: str) -> dict[int, float]:
    seasonality = p["volume"]["seasonality"]
    weights = dict.fromkeys(range(1, 13), 1.0)
    for name, weight in seasonality[p["markets"]["groups"][group]["seasonality"]].items():
        for month in seasonality["months"][name]:
            weights[month] = weight
    return weights


def _submitted_at(rng: Random, year: int, month: int, start: date, end: date) -> datetime:
    first, last = months.span(year, month, start, end)
    minutes = ((last - first).days + 1) * 24 * 60
    return datetime.combine(first, datetime.min.time()) + timedelta(minutes=rng.randrange(minutes))


def _pick(rng: Random, shares: dict[str, float], rest: str) -> str:
    u = rng.random()
    for name, share in shares.items():
        if u < share:
            return name
        u -= share
    return rest


def _travel_answer(rng: Random, p: dict, travel: date) -> str:
    answers = p["form"]["answers"]
    if rng.random() < answers["states_exact_dates"]:
        return travel.isoformat()
    if rng.random() < answers["month_when_no_exact_dates"]:
        return f"{calendar.month_name[travel.month]} {travel.year}"
    if rng.random() < answers["year_when_no_month"]:
        return str(travel.year)
    return form.field(p, "travel_date")["not_sure_answer"]


def _destinations(rng: Random, p: dict) -> str:
    options = [o["label"] for o in form.field(p, "destinations")["options"]]
    count = 1 + draws.poisson(rng, p["form"]["answers"]["countries_named"] - 1)
    chosen = rng.sample(options, min(count, len(options)))
    unsure = form.unsure(p, "destinations")
    return unsure if unsure in chosen else ";".join(o for o in options if o in chosen)


def _heard_about(rng: Random, p: dict, lead: Lead) -> str:
    source = p["volume"]["traffic_source"]
    if rng.random() >= p["form"]["answers"]["answers_how_heard"]:
        return ""
    if lead.repeat_client:
        return form.label(p, "heard_about", source["heard_as_repeat_client"])
    return form.label(p, "heard_about", rng.choice(source["heard_as"][lead.traffic_source]))


def _answer(rng: Random, p: dict, lead: Lead, person: people.Person, form_field: dict) -> str:
    answers = p["form"]["answers"]
    match form_field["role"]:
        case "title":
            return form.label(p, "title", person.title)
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
            return _destinations(rng, p)
        case "travel_date":
            return _travel_answer(rng, p, lead.travel_at.date())
        case "dates_flexible":
            shares = {"fixed": answers["dates_fixed"], "flexible": answers["dates_flexible"]}
            key = _pick(rng, shares, "")
            return form.label(p, "dates_flexible", key) if key else form.unsure(p, "dates_flexible")
        case "newsletter":
            return "Yes" if rng.random() < answers["newsletter_opt_in"] else "No"
        case "nights":
            return form.band(p, "nights", lead.nights)
        case "adults":
            return str(lead.adults)
        case "children":
            return str(lead.children) if lead.children else ""
        case "children_ages":
            ages = p["form"]["party_size"]["child_ages"]
            drawn = sorted(rng.randint(ages["min"], ages["max"]) for _ in range(lead.children))
            return ", ".join(str(age) for age in drawn)
        case "style":
            return form.label(p, "style", lead.style)
        case "budget_per_person":
            stated = rng.random() < answers["states_budget"]
            per_person = lead.budget_per_person_per_night * lead.nights
            return form.band(p, "budget_per_person", per_person) if stated else ""
        case "travelled_before":
            if lead.repeat_client:
                return form.label(p, "travelled_before", "yes")
            enquired = rng.random() < answers["enquired_before"]
            return form.label(p, "travelled_before", "enquired_before" if enquired else "no")
        case "heard_about":
            return _heard_about(rng, p, lead)
        case "message":
            return ""
    raise ValueError(f"the generator does not know the form role {form_field['role']!r}")


def _style(rng: Random, p: dict) -> str:
    """The key of the accommodation style the lead wants; the one not in the mix is the rest."""
    keys = [o["key"] for o in form.field(p, "style")["options"] if "key" in o]
    mix = p["deal"]["style_mix"]
    return _pick(rng, mix, next(k for k in keys if k not in mix))


def _party(rng: Random, p: dict) -> tuple[int, int]:
    """Adults and children; the party type left out of the mix is the rest."""
    size, mix = p["form"]["party_size"], p["form"]["party_mix"]
    adults = size["adults"]
    party = _pick(rng, mix, next(k for k in adults if k not in mix))
    match party:
        case "family":
            return adults[party], 1 + draws.poisson(rng, size["family_children"] - 1)
        case "friends":
            extra = draws.poisson(rng, size["friends_adults"] - adults[party])
            return adults[party] + extra, 0
    return adults[party], 0


def _seasonal_price(p: dict, style: str, travel_month: int) -> float:
    """The style's price per person per night in the travel month.

    The profile's price is the average over the year's travel months, taken as spread evenly over
    the calendar; peak months pay peak_to_low_season_rate times the rest.
    """
    deal = p["deal"]
    peak_months = p["season"]["peak_months"]
    rate = deal["peak_to_low_season_rate"]
    peak_share = len(peak_months) / 12
    low = deal["price_per_person_per_night"][style] / (1 - peak_share + peak_share * rate)
    return low * rate if travel_month in peak_months else low


def countries(p: dict) -> list[dict]:
    """Every country of every source market, each with its name and phone formats."""
    return [c for group in p["markets"]["groups"].values() for c in group["countries"]]


def market_group(rng: Random, p: dict) -> str:
    """A source market drawn from the profile's shares: group A, else group B."""
    return "a" if rng.random() < p["markets"]["group_a_share"] else "b"


def traffic_source(rng: Random, p: dict) -> str:
    """An Original Traffic Source drawn from the profile's mix."""
    source = p["volume"]["traffic_source"]
    others = {k: source[k] for k in source["labels"] if k != source["reference"]}
    return _pick(rng, others, source["reference"])


def _market_shift(p: dict, group: str, multiplier: float) -> float:
    """The factor on a market's median that puts group A at multiplier times group B.

    The share-weighted geometric mean of the two factors is 1, so the profile's own median is the
    median pooled over both markets.
    """
    share_a = p["markets"]["group_a_share"]
    return multiplier ** ((1 - share_a) if group == "a" else -share_a)


def draw_lead(
    rng: Random, p: dict, submitted_at: datetime, group: str, party: tuple[int, int] | None = None
) -> Lead:
    """One Lead submitted at this moment from this market; party fixes its adults and children."""
    deal, process = p["deal"], p["process"]
    trap, answers = p["effects"]["proxy_trap_country"], p["form"]["answers"]
    country = rng.choice(p["markets"]["groups"][group]["countries"])
    source = traffic_source(rng, p)
    repeat_client = rng.random() < p["form"]["answers"]["travelled_before"]
    adults, children = party or _party(rng, p)
    style = _style(rng, p)
    nights = max(1, round(draws.lognormal(rng, deal["nights"], deal["nights_sigma"])))
    cycle_days = draws.lognormal(rng, process["days_to_won_median"], process["days_to_won_sigma"])
    lead_time_months = process["booking_lead_time_months"]
    lead_time_months *= _market_shift(p, group, trap["lead_time_multiplier"])
    lead_time_days = DAYS_PER_MONTH * draws.lognormal(
        rng, lead_time_months, process["booking_lead_time_sigma"]
    )
    travel_at = submitted_at + timedelta(days=cycle_days + lead_time_days)
    price = _seasonal_price(p, style, travel_at.month)
    budget = deal["price_per_person_per_night"][style] * answers["budget_to_style_price"]
    budget *= _market_shift(p, group, trap["budget_multiplier"])
    lead = Lead(
        submitted_at=submitted_at,
        market_group=group,
        country=country["name"],
        traffic_source=source,
        repeat_client=repeat_client,
        style=style,
        nights=nights,
        adults=adults,
        children=children,
        price_per_person_per_night=price,
        budget_per_person_per_night=draws.lognormal(rng, budget, answers["budget_sigma"]),
        cycle_days=cycle_days,
        travel_at=travel_at,
    )
    person = people.draw(rng, p["people"]["titles"], country["phones"])
    answers = {f["label"]: _answer(rng, p, lead, person, f) for f in p["form"]["fields"]}
    return replace(lead, answers=answers)


def draw_leads(rng: Random, p: dict, start: date, end: date) -> list[Lead]:
    """Every lead submitted from start to end (inclusive), at the profile's volume and season."""
    covered = months.covered(start, end)
    markets = p["markets"]
    weights = {group: _month_weights(p, group) for group in markets["groups"]}
    count = round(p["volume"]["leads_per_month"] * sum(share for _, _, share in covered))
    arrivals = []
    for _ in range(count):
        group = market_group(rng, p)
        chances = [weights[group][m] * share for _, m, share in covered]
        year, month, _ = rng.choices(covered, chances)[0]
        arrivals.append((_submitted_at(rng, year, month, start, end), group))
    return [draw_lead(rng, p, at, group) for at, group in sorted(arrivals)]
