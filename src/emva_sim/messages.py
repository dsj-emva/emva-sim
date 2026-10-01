"""The enquiry message: what a Lead writes in "Tell us about your dream trip".

Every word comes from the phrase bank and its cached variations (phrases.py). A message has exactly
the Lead's hidden number of words: blank, a token, or sentences chosen to fill it. Its shape says
which facts it gives (enquiry-forms.md §2): vague, partly or very specific, or a dreamer's. A
phrase is used only where the Lead's facts fit what it requires (facts below), so the text never
contradicts the fields but where a share of messages state a fact differently on purpose. A Lead
with text_commitment writes a decision already made, in one of many wordings; the prohibited
inputs are planted at their shares; a share of the Leads from France write in French, and a share
of those writing English from outside the UK and the US write it imperfectly; a share of messages
are typed all in lower case.
"""

from dataclasses import dataclass, replace
from functools import cache
from random import Random

from emva_sim import form, leads, people
from emva_sim.leads import DatesGiven, Lead
from emva_sim.phrases import Phrase, Phrases, Text, render, words

BLANK, TOKEN, DREAMER = "blank", "token", "dreamer"
VAGUE, PARTLY, VERY = "vague", "partly_specific", "very_specific"
ENGLISH, FRENCH = "en", "fr"
# A bot's spam: a sales pitch with a link, a run of links (phrases), or gibberish (drawn letters).
GIBBERISH, SPAM_SHAPE = "gibberish", "spam"
SPAM = ["pitch", "links", GIBBERISH]
COMMITMENT = "commitment"

# Slots a mention fills: allowed in a message of any shape.
MENTION_SLOTS = {"age", "age2", "child_ages", "companion", "first_name"}
# What each shape may say about the trip, besides the mentions.
SHAPE_SLOTS = {
    VAGUE: {"year"},
    PARTLY: {"adults", "children", "party", "month", "year", "countries", "country"},
    VERY: {
        "adults",
        "children",
        "party",
        "month",
        "year",
        "date",
        "nights",
        "budget",
        "countries",
        "country",
        "park",
    },
}
SHAPE_SLOTS[DREAMER] = SHAPE_SLOTS[VERY]
# Facts the form's fields also hold, which a message may state differently.
FACT_SLOTS = ("adults", "children", "party", "nights", "budget", "month", "year", "date")
# The bank group each way of giving the travel date is written from.
WHEN_GROUPS = {
    DatesGiven.EXACT: "when.exact",
    DatesGiven.MONTH: "when.month",
    DatesGiven.YEAR: "when.year",
    DatesGiven.NOT_SURE: "when.not_sure",
}
# Where each part goes in the message; the fillers mix in the order drawn.
ORDER = [
    "opening",
    "who",
    "when",
    "where",
    "park",
    "style",
    "nights",
    "budget",
    "occasion",
    COMMITMENT,
    "filler",
    "limits",
    "prohibited",
    "question",
    "contact",
    "closing",
]
FILLERS = {
    VAGUE: ["chatter", "question", "contact"],
    PARTLY: ["see", "chatter", "question", "contact"],
    VERY: ["see", "chatter", "question", "contact"],
    DREAMER: ["dreamer", "see", "chatter", "question"],
}
MENTIONS = [
    "ages_of_travellers",
    "named_birthday",
    "retirement",
    "religious_diet",
    "health_or_mobility",
    "pregnancy",
    "sexual_orientation",
    "names_of_travellers",
]
# Mentions that are Intent signals or harmless limits, by their share in [form.answers].
OPTIONAL_MENTIONS = [
    ("occasion", "mentions_occasion"),
    ("limits", "mentions_diet_health_or_mobility"),
]
# Titles that say the writer's gender (the profile's [people].titles keys).
TITLE_GENDER = {"mr": "male", "mrs": "female", "ms": "female", "miss": "female"}


def facts(p: dict, lead: Lead) -> frozenset[str]:
    """What the Lead's fields say, as the tags a phrase can require (see the phrase bank)."""
    found = {
        "solo" if lead.party_size == 1 else "two_or_more",
        "dated" if lead.dates_given in (DatesGiven.EXACT, DatesGiven.MONTH) else "undated",
        "budget" if lead.states_budget else "no_budget",
        "repeat_client" if lead.repeat_client else "first_time",
        "committed" if lead.text_commitment else "uncommitted",
        *(f"to:{country}" for country in lead.destinations),
    }
    if lead.adults >= 2:
        found.add("partner")
    if lead.adults == 2:
        found.add("two_adults")
        if not lead.children:
            found.add("couple")
    if lead.adults >= 3:
        found.add("group")
    if lead.children:
        found.add("children")
    title = form.answer(p, lead.answers, "title")
    keys = {o["label"]: o.get("key") for o in form.field(p, "title")["options"]}
    if keys.get(title) in TITLE_GENDER:
        found.add(TITLE_GENDER[keys[title]])
    return frozenset(found)


@dataclass(frozen=True)
class Candidate:
    """One option of a phrase, rendered for the Lead, with its number of words."""

    phrase: Phrase
    option: str
    text: str
    words: int


@dataclass
class _Part:
    rank: int
    phrase: Phrase
    template: str
    text: str


class _Message:
    """One message being filled to its number of words."""

    def __init__(
        self,
        rng: Random,
        phrases: Phrases,
        base: str,
        target: int,
        values: dict,
        allowed: set,
        known: frozenset[str],
    ):
        self.rng = rng
        self.remaining = target
        self.phrases = phrases
        self.base = base
        self.values = values
        self.allowed = allowed
        self.known = known
        self.parts: list[_Part] = []
        self.used: set[str] = set()
        self.candidates: dict[str, list[Candidate]] = {}

    def _group(self, group: str) -> list[Candidate]:
        """Each phrase of the group the Lead fits, with each of its options, rendered."""
        if group not in self.candidates:
            found = []
            for phrase in self.phrases.group(f"{self.base}.{group}"):
                if phrase.slots <= self.allowed and phrase.requires <= self.known:
                    for option in phrase.options:
                        if phrase.slots:
                            text = render(option, self.values)
                            found.append(Candidate(phrase, option, text, words(text)))
                        else:
                            found.append(Candidate(phrase, option, option, _words(option)))
            self.candidates[group] = found
        return self.candidates[group]

    def options(self, groups: list[str], exactly: int | None = None) -> list[Candidate]:
        """Every candidate of these groups that is unused and fits (or has exactly this many
        words)."""
        return [
            c
            for group in groups
            for c in self._group(group)
            if c.phrase.id not in self.used
            and (c.words == exactly if exactly is not None else c.words <= self.remaining)
        ]

    def add(self, rank: str, candidate: Candidate) -> None:
        self.used.add(candidate.phrase.id)
        self.remaining -= candidate.words
        part = _Part(ORDER.index(rank), candidate.phrase, candidate.option, candidate.text)
        self.parts.append(part)

    def take(self, rank: str, groups: list[str], exactly: int | None = None) -> bool:
        """One phrase from these groups, if one fits."""
        fits = self.options(groups, exactly)
        if not fits:
            return False
        self.add(rank, self.rng.choice(fits))
        return True

    def fill(self, fillers: list[str]) -> None:
        """Fillers until none fits, using a phrase again only once every one has been used."""
        while self.remaining > 0:
            if self.take("filler", fillers):
                continue
            pool = {c.phrase.id for g in fillers for c in self._group(g)}
            if not pool & self.used:
                return
            self.used -= pool
            if not self.take("filler", fillers):
                return

    def close(self) -> None:
        """Make up the last few words with an opening and a closing, else a cut-short sentence."""
        if self.remaining <= 0:
            return
        gap = self.remaining
        if not (self.take("closing", ["closing"], gap) or self.take("opening", ["opening"], gap)):
            self.take("closing", ["closing"])
            if self.remaining > 0:
                self.take("opening", ["opening"])
        if self.remaining > 0:
            usable = [c for c in self._group("chatter") if not c.phrase.slots]
            chosen = self.rng.choice(usable).phrase
            cut = " ".join(chosen.text.split()[: self.remaining])
            self.add("filler", Candidate(chosen, cut, cut, words(cut)))

    def ordered(self) -> list[_Part]:
        return [part for _, part in sorted(enumerate(self.parts), key=lambda e: (e[1].rank, e[0]))]


class Writer:
    """Writes Leads' messages from the profile's phrases."""

    def __init__(self, p: dict, phrases: Phrases):
        self.p = p
        self.phrases = phrases
        self.message_label = form.field(p, "message")["label"]
        self.text = p["text"]
        self.settings = p["form"]["message"]
        self.shape = self.settings["shape"]

    def written(self, lead: Lead, text: Text) -> Lead:
        """The Lead with this message as its answer."""
        return replace(lead, answers={**lead.answers, self.message_label: text.text})

    def bot_message(self, rng: Random, lead: Lead) -> Text:
        """A bot's message: spam at the profile's share, else what the Lead it plays would write."""
        if rng.random() >= self.p["mess"]["bot_spam_message"]:
            return self.message(rng, lead)
        kind = rng.choice(SPAM)
        if kind == GIBBERISH:
            count = self.text["gibberish_words"]
            n = rng.randint(count["min"], count["max"])
            made_up = [people.gibberish(rng, 2, 10) for _ in range(n)]
            return Text(" ".join(made_up), (f"spam.{GIBBERISH}",), shape=SPAM_SHAPE)
        phrase = rng.choice(self.phrases.group(f"spam.{kind}"))
        links = self.text["spam_links"]
        text = render(rng.choice(phrase.options), {"link": lambda: rng.choice(links)})
        return Text(text, (phrase.id,), shape=SPAM_SHAPE)

    def message(self, rng: Random, lead: Lead) -> Text:
        language = ENGLISH
        if lead.country == self.text["french_from"]:
            language = FRENCH if rng.random() < self.settings["written_in_french"] else ENGLISH
        imperfect = (
            language == ENGLISH
            and lead.country in self.text["imperfect_english_from"]
            and rng.random() < self.settings["imperfect_english"]
        )
        lower = rng.random() < self.settings["casual_casing"]
        if lead.message_words == 0:
            return Text("", shape=BLANK)
        base = f"message.{language}"
        known = facts(self.p, lead)
        if lead.message_words <= self.shape["token_words_at_most"]:
            built = _Message(rng, self.phrases, base, lead.message_words, {}, set(), known)
            built.take("filler", ["token"])
            built.close()
            return self._text(built, language, TOKEN, (), None, lower)
        shape = self._shape(rng, lead)
        values = self.values(rng, lead, language)
        allowed = (SHAPE_SLOTS[shape] | MENTION_SLOTS) & set(values)
        built = _Message(rng, self.phrases, base, lead.message_words, values, allowed, known)
        planted = self._required(rng, built, lead)
        self._facts(built, lead, shape)
        fillers = FILLERS[shape] + ([] if lead.text_commitment else ["undecided"])
        built.fill(fillers + (["imperfect"] if imperfect else []))
        built.close()
        disagree = self._disagree(rng, built, lead, language)
        return self._text(built, language, shape, planted, disagree, lower)

    def _text(self, built, language, shape, planted, disagree, lower: bool) -> Text:
        parts = built.ordered()
        cased = (lambda t: t.lower()) if lower else (lambda t: t)
        signal = next((cased(p.text) for p in parts if p.rank == ORDER.index(COMMITMENT)), "")
        return Text(
            cased(" ".join(p.text for p in parts)),
            tuple(p.phrase.id for p in built.parts),
            language,
            shape,
            tuple(planted),
            disagree,
            signal=signal,
        )

    def _shape(self, rng: Random, lead: Lead) -> str:
        if leads.dreamer(self.p, lead):
            return DREAMER
        written = 1 - self.settings["blank_or_token"] - self.settings["dreamer_share"]
        if rng.random() < self.settings["vague_share"] / written:
            return VAGUE
        partly = self.shape["partly_to_very_specific"]
        return PARTLY if rng.random() < partly / (1 + partly) else VERY

    def _required(self, rng: Random, built: _Message, lead: Lead) -> tuple[str, ...]:
        """The decision already made, then each prohibited mention drawn at its share."""
        if lead.text_commitment and not built.take(COMMITMENT, [COMMITMENT]):
            raise ValueError(f"no commitment phrase fits {lead.message_words} words")
        planted = []
        for mention in MENTIONS:
            drawn = rng.random() < self.settings["mentions"][mention]
            if drawn and built.take("prohibited", [f"prohibited.{mention}"]):
                planted.append(mention)
        answers = self.p["form"]["answers"]
        for rank, share in OPTIONAL_MENTIONS:
            if rng.random() < answers[share]:
                built.take(rank, [rank])
        return tuple(planted)

    def _facts(self, built: _Message, lead: Lead, shape: str) -> None:
        if shape == VAGUE:
            built.take("when", ["when.vague"])
            built.take("where", ["where.vague"])
            return
        built.take("who", [f"who.{_party_kind(lead)}"])
        when = WHEN_GROUPS[lead.dates_given]
        if shape == PARTLY and lead.dates_given == DatesGiven.EXACT:
            when = WHEN_GROUPS[DatesGiven.MONTH]
        built.take("when", [when])
        built.take("where", ["where.countries" if lead.destinations else "where.vague"])
        if shape == DREAMER:
            return
        built.take("filler", ["see"])
        built.take("style", ["style"])
        if shape == VERY:
            built.take("park", ["where.park"])
            built.take("nights", ["nights"])
            built.take("budget", ["budget"])

    def values(self, rng: Random, lead: Lead, language: str) -> dict:
        """The slots this Lead can fill, in this language."""
        words_of = self.text["languages"][language]
        names = words_of["countries"]
        ages = self.text["adult_ages"]
        travel = lead.travel_at.date()
        values = {
            "adults": str(lead.adults),
            "party": str(lead.party_size),
            "nights": str(lead.nights),
            "age": str(rng.randint(ages["min"], ages["max"])),
            "age2": str(rng.randint(ages["min"], ages["max"])),
            "companion": rng.choice(people.FIRST_NAMES[rng.choice(sorted(people.FIRST_NAMES))]),
            "first_name": form.answer(self.p, lead.answers, "first_name"),
        }
        if lead.children:
            values["children"] = _children(lead.children, words_of)
            ages_given = form.answer(self.p, lead.answers, "children_ages")
            if ages_given:
                values["child_ages"] = _joined(ages_given.split(", "), words_of["joiner"])
        if lead.dates_given in (DatesGiven.EXACT, DatesGiven.MONTH):
            values["month"] = words_of["months"][travel.month - 1]
        if lead.dates_given != DatesGiven.NOT_SURE:
            values["year"] = str(travel.year)
        if lead.dates_given == DatesGiven.EXACT:
            values["date"] = _date(travel, words_of)
        if lead.states_budget:
            values["budget"] = self.money(lead.budget_per_person, words_of)
        if lead.destinations:
            local = [names.get(c, c) for c in lead.destinations]
            values["countries"] = _joined(local, words_of["joiner"])
            values["country"] = local[0]
            values["park"] = rng.choice(self.text["parks"][rng.choice(lead.destinations)])
        return values

    def money(self, amount: float, words_of: dict) -> str:
        step = self.text["budget_rounded_to"]
        rounded = max(step, step * round(amount / step))
        shown = format(rounded, ",").replace(",", words_of["thousands"])
        return words_of["money"].format(amount=shown)

    def _disagree(self, rng: Random, built: _Message, lead: Lead, language: str) -> str | None:
        """The fact the message states differently from the form, at the profile's share.

        "" when the facts it states agree; None when it states no fact the fields hold. The
        changed fact keeps its number of words, so the message keeps its length.
        """
        stated = [s for s in FACT_SLOTS if any(s in part.phrase.slots for part in built.parts)]
        if not stated:
            return None
        if rng.random() >= self.settings["facts_disagree_with_fields"]:
            return ""
        slot = rng.choice(stated)
        values = dict(built.values)
        values[slot] = self._other(rng, slot, lead, language)
        for part in built.parts:
            if slot in part.phrase.slots:
                part.text = render(part.template, values)
        return slot

    def _other(self, rng: Random, slot: str, lead: Lead, language: str) -> str:
        words_of = self.text["languages"][language]
        travel = lead.travel_at.date()
        match slot:
            case "children":
                return _children(_another(rng, lead.children), words_of)
            case "adults":
                return str(_another(rng, lead.adults))
            case "party":
                return str(_another(rng, lead.party_size))
            case "nights":
                return str(_another(rng, lead.nights))
            case "budget":
                return self.money(lead.budget_per_person * rng.choice([0.5, 2.0]), words_of)
            case "month":
                months = words_of["months"]
                return rng.choice([m for i, m in enumerate(months) if i != travel.month - 1])
            case "year":
                return str(travel.year + rng.choice([-1, 1]))
        shifted = travel.replace(day=1 + (travel.day + 6) % 28)
        return _date(shifted, words_of)


@cache
def _words(option: str) -> int:
    """The words of an option with no slots: the same for every Lead."""
    return words(option)


def _another(rng: Random, n: int) -> int:
    """One more or one fewer, never none."""
    return n + 1 if n <= 1 or rng.random() < 0.5 else n - 1


def _party_kind(lead: Lead) -> str:
    if lead.children:
        return "family"
    if lead.adults <= 1:
        return "solo"
    return "couple" if lead.adults == 2 else "friends"


def _children(n: int, words_of: dict) -> str:
    one, many = words_of["child"]
    return f"{n} {one if n == 1 else many}"


def _joined(items: list[str], joiner: str) -> str:
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + joiner + items[-1]


def _date(day, words_of: dict) -> str:
    return f"{day.day} {words_of['months'][day.month - 1]} {day.year}"
