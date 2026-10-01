"""Made-up people for synthetic leads: names, titles, emails and phone numbers of no real person.

Emails use the domains reserved for examples (RFC 2606). Phone numbers come from the ranges
regulators reserve for fiction: Ofcom's 07700 900xxx, the US 555-01xx and ARCEP's 06 39 98 xx xx.
"""

from dataclasses import dataclass
from random import Random

FIRST_NAMES = {
    "female": [
        "Alice",
        "Charlotte",
        "Emma",
        "Grace",
        "Hannah",
        "Isabel",
        "Julia",
        "Laura",
        "Lucy",
        "Maria",
        "Olivia",
        "Rachel",
        "Sarah",
        "Sophie",
        "Zoe",
        "Camille",
        "Claire",
        "Elena",
    ],
    "male": [
        "Adam",
        "Ben",
        "Daniel",
        "David",
        "Edward",
        "George",
        "Henry",
        "Jack",
        "James",
        "Luke",
        "Mark",
        "Michael",
        "Oliver",
        "Peter",
        "Thomas",
        "Hugo",
        "Louis",
        "Paul",
    ],
}
LAST_NAMES = [
    "Abbott",
    "Bailey",
    "Bennett",
    "Carter",
    "Clarke",
    "Collins",
    "Davies",
    "Dubois",
    "Ellis",
    "Fisher",
    "Foster",
    "Garnier",
    "Gray",
    "Hayes",
    "Hughes",
    "Jordan",
    "Kelly",
    "Lambert",
    "Lewis",
    "Marsh",
    "Martin",
    "Mitchell",
    "Morel",
    "Murray",
    "Parker",
    "Porter",
    "Reed",
    "Roux",
    "Russell",
    "Shaw",
    "Stone",
    "Turner",
    "Walsh",
    "Ward",
    "Webb",
    "Young",
]
TITLES = {
    "female": ["Mrs", "Mrs", "Ms", "Ms", "Miss", "Dr"],
    "male": ["Mr", "Mr", "Mr", "Mr", "Dr"],
}
EMAIL_DOMAINS = ["example.com", "example.org", "example.net"]
US_AREA_CODES = ["212", "312", "415", "617", "303"]


@dataclass(frozen=True)
class Person:
    title: str
    first_name: str
    last_name: str
    email: str
    phone: str


def _phone(rng: Random, country: str) -> str:
    if country == "United Kingdom":
        return f"+44 7700 900{rng.randrange(1000):03d}"
    if country == "United States":
        return f"+1 ({rng.choice(US_AREA_CODES)}) 555-01{rng.randrange(100):02d}"
    if country == "France":
        return f"+33 6 39 98 {rng.randrange(100):02d} {rng.randrange(100):02d}"
    raise ValueError(f"no fictional phone range for {country}")


def draw(rng: Random, country: str) -> Person:
    gender = rng.choice(["female", "male"])
    first = rng.choice(FIRST_NAMES[gender])
    last = rng.choice(LAST_NAMES)
    email = f"{first}.{last}{rng.randrange(100)}@{rng.choice(EMAIL_DOMAINS)}".lower()
    return Person(rng.choice(TITLES[gender]), first, last, email, _phone(rng, country))
