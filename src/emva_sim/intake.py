"""Mess at intake: every submission the sales system receives, and what it holds of each.

Besides the genuine Leads come duplicates (the same person again, or through a second channel) and
bot or spam submissions, at the profile's shares of all rows (neglect-and-mess.md §5). None of it
touches a Lead or its true path: the mess is in the copy the sales system holds.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from random import Random

from emva_sim import form, leads
from emva_sim.leads import Lead
from emva_sim.people import EMAIL_DOMAINS

LEAD = "lead"
DUPLICATE = "duplicate"


@dataclass(frozen=True)
class Submission:
    """One form submission as the sales system holds it: one deal and one contact.

    lead is the index of the Lead it is, or of the Lead a duplicate repeats.
    """

    kind: str
    lead: int
    submitted_at: datetime
    answers: dict[str, str]
    traffic_source: str
    repeat_client: bool
    travel_month: str


def submissions(rng: Random, p: dict, drawn: list[Lead], until: datetime) -> list[Submission]:
    """Every submission received before until (the end of the history), in order of arrival."""
    mess = p["mess"]
    genuine_share = 1 - mess["duplicate_leads"] - mess["bot_or_spam"]
    received = []
    for i, lead in enumerate(drawn):
        received.append(_genuine(i, lead))
        if rng.random() < mess["duplicate_leads"] / genuine_share:
            again = _duplicate(rng, p, i, lead)
            if again.submitted_at < until:
                received.append(again)
    return sorted(received, key=lambda s: s.submitted_at)


def _genuine(i: int, lead: Lead) -> Submission:
    return Submission(
        LEAD,
        i,
        lead.submitted_at,
        dict(lead.answers),
        lead.traffic_source,
        lead.repeat_client,
        f"{lead.travel_at:%b}",
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
