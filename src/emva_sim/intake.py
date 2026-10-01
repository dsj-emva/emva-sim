"""Mess at intake: every submission the sales system receives, and what it holds of each.

Besides the genuine Leads come duplicates (the same person again, or through a second channel) and
bot or spam submissions, at the profile's shares of all rows (neglect-and-mess.md §5). None of it
touches a Lead or its true path: the mess is in the copy the sales system holds.
"""

import calendar
import math
import re
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from random import Random

from emva_sim import form, leads
from emva_sim.leads import Lead
from emva_sim.people import EMAIL_DOMAINS

LEAD = "lead"
DUPLICATE = "duplicate"
BOT = "bot or spam"
# Throwaway addresses under the TLD reserved for examples (RFC 2606), so none is a real service.
DISPOSABLE_DOMAINS = ["tempinbox.example", "throwmail.example", "10minutemail.example"]
SPAM_PITCHES = [
    "Grow your website traffic fast, first page of search guaranteed",
    "Cheap backlinks and guest posts for your travel website",
    "We build apps and websites at low cost, reply for a free quote",
    "Earn money from home with this investment, returns every week",
]


@dataclass(frozen=True)
class Submission:
    """One form submission as the sales system holds it: one deal and one contact.

    lead is the index of the Lead it is, or of the Lead a duplicate repeats; a bot has none.
    """

    kind: str
    lead: int | None
    submitted_at: datetime
    answers: dict[str, str]
    traffic_source: str
    repeat_client: bool
    travel_month: str
    invalid_email: bool = False
    invalid_phone: bool = False
    missing_or_wrong: tuple[str, ...] = ()  # labels of the key fields held blank or wrong


def submissions(
    rng: Random, p: dict, drawn: list[Lead], start: datetime, until: datetime
) -> list[Submission]:
    """Every submission received from start to until (the history), in order of arrival."""
    mess = p["mess"]
    genuine_share = 1 - mess["duplicate_leads"] - mess["bot_or_spam"]
    received = []
    for i, lead in enumerate(drawn):
        received.append(_genuine(rng, p, i, lead))
        if rng.random() < mess["duplicate_leads"] / genuine_share:
            again = _duplicate(rng, p, i, lead)
            if again.submitted_at < until:
                received.append(again)
        if rng.random() < mess["bot_or_spam"] / genuine_share:
            received.append(_bot(rng, p, start + (until - start) * rng.random()))
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
        missing = rng.random() < 0.5
        answers[label] = "" if missing else _wrong(rng, p, key_field, answers[label], lead)
        altered = (label,)
    return Submission(
        LEAD,
        i,
        lead.submitted_at,
        answers,
        lead.traffic_source,
        lead.repeat_client,
        f"{lead.travel_at:%b}",
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
            return str(n + 1 if n <= 1 or rng.random() < 0.5 else n - 1)
        case "country":
            countries = [c["name"] for g in p["markets"]["groups"].values() for c in g["countries"]]
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


def _duplicate(rng: Random, p: dict, i: int, lead: Lead) -> Submission:
    """The same person submitting again some days later, perhaps through another channel.

    HubSpot merges contacts by email, so a duplicate that becomes a second contact has another
    address: an alias, another domain or a slip. Its name may be typed in another case.
    """
    median = p["mess"]["duplicate_days_later"]
    later = lead.submitted_at + timedelta(days=rng.expovariate(math.log(2) / median))
    answers = dict(lead.answers)
    email = form.field(p, "email")["label"]
    answers[email] = _other_address(rng, answers[email])
    if rng.random() < 0.5:
        case = rng.choice([str.lower, str.upper])
        for role in ("first_name", "last_name"):
            label = form.field(p, role)["label"]
            answers[label] = case(answers[label])
    return Submission(
        DUPLICATE,
        i,
        later,
        answers,
        leads.traffic_source(rng, p),
        lead.repeat_client,
        f"{lead.travel_at:%b}",
    )


def _bot(rng: Random, p: dict, at: datetime) -> Submission:
    """A bot or spam submission: made-up names, a disposable address, junk or no message."""
    answers = {f["label"]: _bot_answer(rng, p, f, at) for f in p["form"]["fields"]}
    return Submission(
        BOT,
        None,
        at.replace(second=0, microsecond=0),
        answers,
        leads.traffic_source(rng, p),
        False,
        calendar.month_abbr[rng.randint(1, 12)],
    )


def _bot_answer(rng: Random, p: dict, form_field: dict, at: datetime) -> str:
    options = [o["label"] for o in form_field.get("options", [])]
    match form_field["role"], form_field["kind"]:
        case (("first_name" | "last_name"), _):
            return _gibberish(rng).capitalize()
        case _, "email":
            return f"{_gibberish(rng)}{rng.randrange(1000)}@{rng.choice(DISPOSABLE_DOMAINS)}"
        case _, "phone":
            return rng.choice(["", "1234567890", str(rng.randrange(10**5, 10**6))])
        case _, "country":
            countries = [c for g in p["markets"]["groups"].values() for c in g["countries"]]
            return rng.choice(countries)["name"]
        case _, "month_year":
            month = calendar.month_name[rng.randint(1, 12)]
            return rng.choice([form_field["not_sure_answer"], f"{month} {at.year}"])
        case "adults", _:
            return str(rng.choice([0, rng.randint(25, 99), rng.randint(1, 4)]))
        case "children", _:
            return rng.choice(["", str(rng.randint(13, 40))])
        case _, "long_text":
            return rng.choice(["", _spam(rng), _gibberish(rng)])
        case _, "checkbox":
            return rng.choice(["Yes", "No"])
        case _, ("choice" | "multi"):
            return rng.choice(options if form_field["required"] else ["", *options])
    return ""


def _gibberish(rng: Random) -> str:
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(5, 10)))


def _spam(rng: Random) -> str:
    links = " ".join(f"https://{_gibberish(rng)}.example/{_gibberish(rng)}" for _ in range(3))
    return f"{rng.choice(SPAM_PITCHES)} {links}"


def _other_address(rng: Random, email: str) -> str:
    local, domain = email.split("@")
    variants = [
        f"{local}+travel@{domain}",
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
