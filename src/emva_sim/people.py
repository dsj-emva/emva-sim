"""Made-up people for synthetic leads: names, emails and phone numbers of no real person.

The name lists are generic synthetic names, drawn independently of the market, so they are not an
industry fact and carry no planted signal. Emails use the domains reserved for examples (RFC 2606);
titles and phone formats come from the profile.
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
EMAIL_DOMAINS = ["example.com", "example.org", "example.net"]
# Throwaway addresses as bots give them, under the TLD reserved for examples, so none is real.
THROWAWAY_DOMAINS = ["tempinbox.example", "throwmail.example", "10minutemail.example"]


@dataclass(frozen=True)
class Person:
    title: str
    first_name: str
    last_name: str
    email: str
    phone: str


def _phone(rng: Random, formats: list[str]) -> str:
    return "".join(str(rng.randrange(10)) if c == "#" else c for c in rng.choice(formats))


def draw(rng: Random, titles: dict[str, dict[str, float]], phone_formats: list[str]) -> Person:
    """A made-up person; titles are weights by gender, phone formats use "#" for any digit."""
    gender = rng.choice(sorted(titles))
    first = rng.choice(FIRST_NAMES[gender])
    last = rng.choice(LAST_NAMES)
    email = f"{first}.{last}{rng.randrange(100)}@{rng.choice(EMAIL_DOMAINS)}".lower()
    weights = titles[gender]
    title = rng.choices(list(weights), list(weights.values()))[0]
    return Person(title, first, last, email, _phone(rng, phone_formats))
