"""The profile's phrase bank and the cache of its model-written variations.

The bank is a TOML file beside the profile; every list in it is a group of phrases, named by its
dotted path. A phrase is a string, or a table with its text and the facts about the Lead it
requires (e.g. a party of two or more), so the text never contradicts the Lead's fields. Each
phrase is sent once to a language model (vary.py), which writes natural variations of it; the
cache keeps them, keyed by a hash of the phrase's text, with the model that wrote them. A phrase
that carries a planted signal has each variation checked, by a second question to the model, to
say what the phrase says; the check is cached too.

Generation reads only the cache and never calls the model. Every cached entry is checked again
when the cache is loaded; a phrase with no valid cached variations stops generation.
"""

import hashlib
import json
import re
import tomllib
from collections import Counter
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

VARY_COMMAND = "make vary-phrases"
SLOT = re.compile(r"\{(\w+)\}")
# Tables of the bank that are not phrases: what each kind of text is, for the model, and what each
# group carrying a planted signal says, for the check of its variations.
ABOUT, MEANING = "about", "meaning"
YES = "yes"
# A capitalised word a variation may add: "I" and its contractions, in English and French.
PRONOUNS = re.compile(r"^(I|I'\w+|J'\w+|Je)$")
SENTENCE_END = re.compile(r"[.!?:;]$")


class MissingVariations(RuntimeError):
    pass


class InvalidVariations(ValueError):
    pass


def key(text: str) -> str:
    """The cache's key for a phrase: a hash of its text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def slots(text: str) -> list[str]:
    """The slots a phrase names, in order, once per time it names them."""
    return SLOT.findall(text)


def words(text: str) -> int:
    return len(text.split())


@dataclass(frozen=True)
class BankPhrase:
    id: str
    text: str
    requires: frozenset[str]

    @property
    def group(self) -> str:
        return self.id.split("#")[0]


@dataclass(frozen=True)
class Phrase:
    """One phrase of the bank, with the texts generation may write for it: itself and its
    cached variations, and the facts about the Lead it requires."""

    id: str
    text: str
    options: tuple[str, ...]
    requires: frozenset[str] = frozenset()

    @cached_property
    def slots(self) -> frozenset[str]:
        return frozenset(slots(self.text))


def bank_phrases(bank: dict) -> list[BankPhrase]:
    """Every phrase of the bank, in the bank's order; an id is its group and its place in it,
    e.g. "message.en.who.couple#2"."""
    found = []

    def walk(node, path):
        if isinstance(node, list):
            group = ".".join(path)
            for i, entry in enumerate(node, start=1):
                text = entry if isinstance(entry, str) else entry["text"]
                requires = frozenset(() if isinstance(entry, str) else entry["requires"])
                found.append(BankPhrase(f"{group}#{i}", text, requires))
        elif isinstance(node, dict):
            for name, value in node.items():
                walk(value, (*path, name))

    walk({k: v for k, v in bank.items() if k not in (ABOUT, MEANING)}, ())
    return found


def meaning(bank: dict, group: str) -> str | None:
    """What the group's phrases say, if the group carries a planted signal."""
    return bank.get(MEANING, {}).get(group)


def paths(profile_path: Path, raw: dict) -> tuple[Path, Path]:
    """The phrase bank and the cache the profile names, beside the profile."""
    folder = Path(profile_path).parent
    return folder / raw["text"]["phrase_bank"], folder / raw["text"]["variations"]


def load_bank(path: Path) -> dict:
    return tomllib.loads(Path(path).read_text(encoding="utf-8"))


def read_cache(path: Path, model: str) -> dict:
    path = Path(path)
    if not path.exists():
        return {"model": model, "phrases": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_cache(path: Path, cache: dict) -> None:
    """Write the cache with its keys sorted, so a run that adds nothing changes nothing."""
    text = json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True)
    Path(path).write_text(text + "\n", encoding="utf-8")


def _allowed_words(count: int) -> tuple[int, int]:
    slack = max(2, count // 2)
    return max(1, count - slack), count + slack


def _new_capitals(phrase: str, variation: str) -> list[str]:
    """Capitalised words of the variation that the phrase lacks, but at a sentence's start."""
    known = set(re.findall(r"[^\W\d_][\w'-]*", phrase))
    found, starts = [], True
    for token in variation.split():
        word = token.strip("\"'()[]«»,.!?:;")
        if word[:1].isupper() and not starts and word not in known and not PRONOUNS.match(word):
            found.append(word)
        starts = bool(SENTENCE_END.search(token))
    return found


def check(phrase: str, variations, n: int) -> list[str]:
    """The variations, if every rule holds; InvalidVariations says which one broke.

    Each of the n variations is one line, not the phrase itself and not given twice, keeps the
    phrase's slots exactly, is near its length, and adds no number and no capitalised word (a
    name, a place) the phrase lacks.
    """
    if not isinstance(variations, list) or not all(isinstance(v, str) for v in variations):
        raise InvalidVariations("the variations are not a list of strings")
    found = [v.strip() for v in variations]
    if len(found) != n:
        raise InvalidVariations(f"asked for {n} variations, got {len(found)}")
    low, high = _allowed_words(words(phrase))
    wanted = Counter(slots(phrase))
    digits = set(re.findall(r"\d+", SLOT.sub("", phrase)))
    for v in found:
        if not v:
            raise InvalidVariations("a variation is empty")
        if v.splitlines() != [v] or "\r" in v:
            raise InvalidVariations(f"a variation is not one line: {v!r}")
        if v == phrase.strip():
            raise InvalidVariations("a variation is the phrase itself")
        braces = v.count("{") == v.count("}") == sum(wanted.values())
        if Counter(slots(v)) != wanted or not braces:
            raise InvalidVariations(f"a variation does not keep the phrase's slots: {v!r}")
        if not low <= words(v) <= high:
            raise InvalidVariations(f"a variation has {words(v)} words, not {low} to {high}")
        if set(re.findall(r"\d+", SLOT.sub("", v))) - digits:
            raise InvalidVariations(f"a variation adds a number: {v!r}")
        if added := _new_capitals(phrase, v):
            raise InvalidVariations(f"a variation adds the capitalised words {added}: {v!r}")
    if len(set(found)) != len(found):
        raise InvalidVariations("a variation is given twice")
    return found


def check_entry(bank: dict, phrase: BankPhrase, entry: dict | None, model: str, n: int) -> None:
    """The cached entry is the given model's, its variations pass every rule, and, for a phrase
    carrying a planted signal, the model said each variation says what the phrase says."""
    if entry is None:
        raise InvalidVariations("no cached variations")
    if entry.get("model") != model:
        raise InvalidVariations(f"cached by {entry.get('model')!r}, not {model!r}")
    check(phrase.text, entry["variations"], n)
    said = meaning(bank, phrase.group)
    if said is not None:
        checked = entry.get("meaning_check", {})
        if checked.get("statement") != said or checked.get("answers") != [YES] * n:
            raise InvalidVariations(f"its variations are not all checked to say: {said}")


@dataclass(frozen=True)
class Text:
    """A piece of generated text and, for the Hidden truth, how it was made: the phrases it used,
    its language, and what was planted in it."""

    text: str
    phrase_ids: tuple[str, ...] = ()
    language: str = ""
    shape: str = ""
    mentions: tuple[str, ...] = ()
    fact_differs: str | None = None  # the fact stated unlike the form; "" if none
    abbreviated: bool | None = None
    typo: bool | None = None
    signal: str = ""  # the sentence carrying a planted signal, as written before any typo


def render(template: str, values: dict) -> str:
    """The template with each slot filled; a callable value is called once per slot it fills."""

    def fill(match):
        value = values[match.group(1)]
        return value() if callable(value) else value

    return SLOT.sub(fill, template)


class Phrases:
    """The bank's groups, each phrase with its cached variations."""

    def __init__(self, bank: dict, cache: dict, model: str, n: int):
        cached = cache["phrases"]
        unusable = []
        for phrase in bank_phrases(bank):
            try:
                check_entry(bank, phrase, cached.get(key(phrase.text)), model, n)
            except InvalidVariations as error:
                unusable.append((phrase, error))
        if unusable:
            first, error = unusable[0]
            raise MissingVariations(
                f"{len(unusable)} phrases of the phrase bank have no valid cached variations"
                f" (the first is {first.id}: {first.text!r}, {error}). Generation never makes"
                f" up model output: run `{VARY_COMMAND}` with ANTHROPIC_API_KEY set and commit"
                " the cache."
            )
        self.groups: dict[str, list[Phrase]] = {}
        for p in bank_phrases(bank):
            options = (p.text, *cached[key(p.text)]["variations"])
            self.groups.setdefault(p.group, []).append(Phrase(p.id, p.text, options, p.requires))

    @classmethod
    def load(cls, profile_path: Path, raw: dict) -> "Phrases":
        bank, cache = paths(profile_path, raw)
        text = raw["text"]
        cached = read_cache(cache, text["model"])
        return cls(load_bank(bank), cached, text["model"], text["variations_per_phrase"])

    def group(self, name: str) -> list[Phrase]:
        return self.groups[name]
