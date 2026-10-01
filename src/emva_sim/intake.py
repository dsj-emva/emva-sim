"""Mess at intake: every submission the sales system receives, and what it holds of each.

Besides the genuine Leads come duplicates (the same person again, or through a second channel) and
bot or spam submissions, at the profile's shares of all rows (neglect-and-mess.md §5). None of it
touches a Lead or its true path: the mess is in the copy the sales system holds.
"""

import calendar
import re
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from random import Random

from emva_sim import draws, form, leads
from emva_sim.leads import Lead
from emva_sim.people import EMAIL_DOMAINS, THROWAWAY_DOMAINS


class RowKind(StrEnum):
    """What a row of the export is; only a genuine Lead has a true path and an Outcome."""

    LEAD = "lead"
    DUPLICATE = "duplicate"
    BOT = "bot or spam"


@dataclass(frozen=True)
class Submission:
    """One form submission as the sales system holds it: one deal and one contact.

    lead is the Lead it is or repeats, or the made-up one a bot plays; index is that Lead's place
    among the drawn Leads (None for a bot). traffic_source is the contact's, which a duplicate
    on a second contact does not share with its Lead.
    """

    kind: RowKind
    lead: Lead
    index: int | None
    submitted_at: datetime
    answers: dict[str, str]
    traffic_source: str
    invalid_email: bool = False
    invalid_phone: bool = False
    missing_or_wrong: tuple[str, ...] = ()  # labels of the key fields held blank or wrong
    new_contact: bool = True  # False for a duplicate HubSpot puts on its Lead's contact


def submissions(
    rng: Random, p: dict, drawn: list[Lead], start: datetime, until: datetime
) -> list[Submission]:
    """Every submission received from start to until (the history), in order of arrival.

    Each Lead brings a duplicate with chance d / (1 - d - b) and a bot with chance b / (1 - d - b),
    so duplicates (d) and bots (b) are their profile shares of all rows. A duplicate that would
    arrive after the history is not received.
    """
    mess = p["mess"]
    genuine_share = 1 - mess["duplicate_leads"] - mess["bot_or_spam"]
    received = []
    for i, lead in enumerate(drawn):
        held = _genuine(rng, p, i, lead)
        received.append(held)
        if rng.random() < mess["duplicate_leads"] / genuine_share:
            again = _duplicate(rng, p, held)
            if again.submitted_at < until:
                received.append(again)
        if rng.random() < mess["bot_or_spam"] / genuine_share:
            at = start + (until - start) * rng.random()
            received.append(_bot(rng, p, at.replace(second=0, microsecond=0)))
    return sorted(received, key=lambda s: s.submitted_at)


def _genuine(rng: Random, p: dict, i: int, lead: Lead) -> Submission:
    """A Lead as the sales system holds it: email or phone invalid, a key field blank or wrong."""
    mess = p["mess"]
    answers = dict(lead.answers)
    email, phone = form.field(p, "email")["label"], form.field(p, "phone")["label"]
    invalid_email = rng.random() < mess["invalid_email"]
    if invalid_email:
        answers[email] = _broken_address(rng, answers[email])
    invalid_phone = bool(answers[phone]) and rng.random() < mess["invalid_phone"]
    if invalid_phone:
        answers[phone] = _broken_phone(rng, answers[phone])
    altered = ()
    if rng.random() < mess["field_missing_or_wrong"]:
        filled = [form.field(p, role) for role in mess["key_fields"]]
        key_field = rng.choice([f for f in filled if answers[f["label"]]])
        label = key_field["label"]
        missing = rng.random() < mess["missing_rather_than_wrong"]
        answers[label] = "" if missing else _wrong(rng, p, key_field, answers[label], lead)
        altered = (label,)
    return Submission(
        RowKind.LEAD,
        lead,
        i,
        lead.submitted_at,
        answers,
        lead.traffic_source,
        invalid_email,
        invalid_phone,
        altered,
    )


def _wrong(rng: Random, p: dict, form_field: dict, value: str, lead: Lead) -> str:
    """Another plausible value than the one the lead gave: a slip, a neighbour, another option."""
    match form_field["kind"]:
        case "choice" | "multi":
            return rng.choice([o["label"] for o in form_field["options"] if o["label"] != value])
        case "number":
            n = int(value)
            one_more = n <= 1 or rng.random() < p["mess"]["wrong_number_one_more"]
            return str(n + 1 if one_more else n - 1)
        case "country":
            countries = [c["name"] for c in leads.countries(p)]
            return rng.choice([c for c in countries if c != value])
        case "month_year":
            if year := re.search(r"\d{4}", value):
                shifted = str(int(year.group()) + rng.choice([-1, 1]))
                return value[: year.start()] + shifted + value[year.end() :]
            return f"{calendar.month_name[rng.randint(1, 12)]} {lead.travel_at.year}"
    slipped = _slip(rng, value)
    return slipped if slipped != value else value + value[-1]


def _broken_address(rng: Random, email: str) -> str:
    """An address no mail can reach: the @ left out or doubled, a dot or a space gone wrong."""
    local, domain = email.split("@")
    return rng.choice(
        [
            f"{local}{domain}",
            f"{local}@@{domain}",
            f"{local}@{domain.replace('.', '', 1)}",
            f"{local}@{domain.replace('.', ',', 1)}",
            f"{local} @{domain}",
        ]
    )


def _broken_phone(rng: Random, phone: str) -> str:
    """A number no call can reach: cut short, too long, a letter for a digit, or all zeros."""
    digits = [i for i, c in enumerate(phone) if c.isdigit()]
    i = rng.choice(digits)
    return rng.choice(
        [
            phone[: digits[-4]].rstrip(),
            f"{phone}{rng.randrange(100, 1000)}",
            f"{phone[:i]}O{phone[i + 1 :]}",
            "0" * len(digits),
        ]
    )


def _duplicate(rng: Random, p: dict, held: Submission) -> Submission:
    """The same person submitting again some days later, perhaps through another channel.

    HubSpot merges contacts by email: a duplicate giving the address the contact holds becomes a
    second deal on that contact; one giving another address (an alias, another domain or a slip)
    becomes a second contact, with a traffic source of its own. Its name may be typed in another
    case.
    """
    mess, lead = p["mess"], held.lead
    later = lead.submitted_at + timedelta(days=draws.exponential(rng, mess["duplicate_days_later"]))
    answers = dict(lead.answers)
    email = form.field(p, "email")["label"]
    same_email = rng.random() < mess["duplicate_same_email"]
    answers[email] = (
        held.answers[email]
        if same_email
        else _other_address(rng, answers[email], mess["email_alias_tag"])
    )
    if rng.random() < mess["duplicate_name_case_changed"]:
        case = rng.choice([str.lower, str.upper])
        for role in ("first_name", "last_name"):
            label = form.field(p, role)["label"]
            answers[label] = case(answers[label])
    source = held.traffic_source if same_email else leads.traffic_source(rng, p)
    return Submission(
        RowKind.DUPLICATE, lead, held.index, later, answers, source, new_contact=not same_email
    )


def _bot(rng: Random, p: dict, at: datetime) -> Submission:
    """A bot or spam submission, answering the form as a made-up Lead would.

    Only the profile's shares of bots give a made-up name, a throwaway address or an impossible
    party, so no one sign gives every bot away.
    """
    mess = p["mess"]
    party = None
    if rng.random() < mess["bot_impossible_party"]:
        shape = rng.choice(mess["impossible_party"])
        party = (_between(rng, shape["adults"]), _between(rng, shape["children"]))
    lead = leads.draw_lead(rng, p, at, leads.market_group(rng, p), party)
    answers = dict(lead.answers)
    first, last, email = (
        form.field(p, role)["label"] for role in ("first_name", "last_name", "email")
    )
    made_up = rng.random() < mess["bot_made_up_name"]
    if made_up:
        answers[first], answers[last] = _gibberish(rng).capitalize(), _gibberish(rng).capitalize()
    throwaway = rng.random() < mess["bot_throwaway_email"]
    if made_up or throwaway:
        domain = rng.choice(THROWAWAY_DOMAINS if throwaway else EMAIL_DOMAINS)
        local = f"{answers[first]}.{answers[last]}{rng.randrange(100)}".lower()
        answers[email] = f"{local}@{domain}"
    return Submission(RowKind.BOT, lead, None, at, answers, lead.traffic_source)


def _between(rng: Random, bounds: dict) -> int:
    return rng.randint(bounds["min"], bounds["max"])


def _gibberish(rng: Random) -> str:
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(5, 10)))


def _other_address(rng: Random, email: str, alias_tag: str) -> str:
    local, domain = email.split("@")
    variants = [
        f"{local}+{alias_tag}@{domain}",
        f"{local.replace('.', '')}@{domain}",
        f"{local}@{rng.choice([d for d in EMAIL_DOMAINS if d != domain])}",
        f"{_slip(rng, local)}@{domain}",
    ]
    return rng.choice([v for v in variants if v != email])


def _slip(rng: Random, text: str) -> str:
    """Two neighbouring characters typed the wrong way round, or one left out."""
    if len(text) < 3:
        return text + text[-1:]
    i = rng.randrange(len(text) - 1)
    if rng.random() < 0.5 and text[i] != text[i + 1]:
        return text[:i] + text[i + 1] + text[i] + text[i + 2 :]
    return text[:i] + text[i + 1 :]
