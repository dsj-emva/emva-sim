"""The profile's phrase bank and the cache of its model-written variations.

The bank is a TOML file beside the profile; every list of strings in it is a group of phrases,
named by its dotted path. Each phrase was sent once to a language model (vary.py), which wrote
natural variations of it; the cache keeps them, keyed by a hash of the phrase's text. Generation
reads only the cache and never calls the model: a phrase with no cached variations stops it.
"""

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

VARY_COMMAND = "make vary-phrases"
SLOT = re.compile(r"\{(\w+)\}")
# The bank's table describing each kind of text for the model; not phrases.
ABOUT = "about"


class MissingVariations(RuntimeError):
    pass


def key(text: str) -> str:
    """The cache's key for a phrase: a hash of its text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def slots(text: str) -> list[str]:
    """The slots a phrase names, in order, once per time it names them."""
    return SLOT.findall(text)


@dataclass(frozen=True)
class Phrase:
    """One phrase of the bank, with the texts generation may write for it: itself and its
    cached variations."""

    id: str
    text: str
    options: tuple[str, ...]

    @cached_property
    def slots(self) -> frozenset[str]:
        return frozenset(slots(self.text))


def bank_phrases(bank: dict) -> list[tuple[str, str]]:
    """Every phrase of the bank as (id, text), in the bank's order; an id is its group and its
    place in it, e.g. "message.en.who.couple#2"."""
    found = []

    def walk(node, path):
        if isinstance(node, list):
            group = ".".join(path)
            found.extend((f"{group}#{i}", text) for i, text in enumerate(node, start=1))
        elif isinstance(node, dict):
            for name, value in node.items():
                walk(value, (*path, name))

    walk({k: v for k, v in bank.items() if k != ABOUT}, ())
    return found


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


def words(text: str) -> int:
    return len(text.split())


def render(template: str, values: dict) -> str:
    """The template with each slot filled; a callable value is called once per slot it fills."""

    def fill(match):
        value = values[match.group(1)]
        return value() if callable(value) else value

    return SLOT.sub(fill, template)


class Phrases:
    """The bank's groups, each phrase with its cached variations."""

    def __init__(self, bank: dict, cache: dict):
        cached = cache["phrases"]
        missing = [(pid, text) for pid, text in bank_phrases(bank) if key(text) not in cached]
        if missing:
            raise MissingVariations(
                f"{len(missing)} phrases of the phrase bank have no cached variations"
                f" (the first is {missing[0][0]}: {missing[0][1]!r}). Generation never makes"
                f" up model output: run `{VARY_COMMAND}` with ANTHROPIC_API_KEY set and commit"
                " the cache."
            )
        self.groups: dict[str, list[Phrase]] = {}
        for pid, text in bank_phrases(bank):
            options = (text, *cached[key(text)]["variations"])
            self.groups.setdefault(pid.split("#")[0], []).append(Phrase(pid, text, options))

    @classmethod
    def load(cls, profile_path: Path, raw: dict) -> "Phrases":
        bank, cache = paths(profile_path, raw)
        return cls(load_bank(bank), read_cache(cache, raw["text"]["model"]))

    def group(self, name: str) -> list[Phrase]:
        return self.groups[name]
