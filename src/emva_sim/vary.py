"""vary-phrases: have a language model rewrite each bank phrase once into natural variations.

Each phrase missing from the cache is sent once; the reply is checked (the asked number of
distinct, one-line variations, each keeping every slot and close to the phrase's length) and only
a reply that passes is cached. Generation reads the cache and never calls the model, so runs stay
reproducible from the seed.
"""

import json
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import anthropic

from emva_sim import phrases, profile

KEY_NAME = "ANTHROPIC_API_KEY"
LANGUAGES = {"fr": "French"}
DEFAULT_LANGUAGE = "English"

SYSTEM = """You write variations of one phrase for a generator of synthetic sales data.
The phrase is {about}, written in {language}.

Write {n} variations of it, each as a real person might have written it instead. Rules:
- Keep the meaning exactly. Add no fact: no new number, name, place, date, amount, person or reason.
- Keep every placeholder in curly braces, such as {{month}}, exactly as written, as many times as it
  appears; write no other curly braces.
- Write in {language}, in the same voice, and about as long as the phrase.
- Vary the wording freely: where a natural synonym or another construction exists, use it
  rather than repeating the phrase's key words.
- One line each, no numbering, no quotation marks around them.

Reply with JSON: {{"variations": [...]}}."""

SCHEMA = {
    "type": "object",
    "properties": {"variations": {"type": "array", "items": {"type": "string"}}},
    "required": ["variations"],
    "additionalProperties": False,
}


class NoApiKey(RuntimeError):
    pass


class InvalidReply(ValueError):
    pass


@dataclass(frozen=True)
class Request:
    phrase: str
    about: str
    language: str
    n: int


class Client(Protocol):
    model: str

    def variations(self, request: Request) -> str:
        """The model's reply: JSON holding the variations."""


class HaikuClient:
    """Claude Haiku 4.5 through the Anthropic SDK."""

    def __init__(self, key: str, model: str):
        self.model = model
        self.client = anthropic.Anthropic(api_key=key)

    def variations(self, request: Request) -> str:
        system = SYSTEM.format(about=request.about, language=request.language, n=request.n)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": request.phrase}],
            output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        )
        return "".join(block.text for block in response.content if block.type == "text")


def api_key(environ: Mapping[str, str], env_file: Path) -> str:
    """The API key from the environment, else from a local .env file (KEY=value lines)."""
    if environ.get(KEY_NAME):
        return environ[KEY_NAME]
    env_file = Path(env_file)
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.strip().partition("=")
            if sep and name.strip() == KEY_NAME and value.strip():
                return value.strip().strip("\"'")
    raise NoApiKey(f"set {KEY_NAME} in the environment or in a local .env file")


def _allowed_words(words: int) -> tuple[int, int]:
    slack = max(2, words // 2)
    return max(1, words - slack), words + slack


def validate(phrase: str, reply: str, n: int) -> list[str]:
    """The variations in the reply, if every rule holds; InvalidReply says which one broke."""
    try:
        found = json.loads(reply)["variations"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise InvalidReply(f"the reply is not the asked JSON ({error})") from error
    if not isinstance(found, list) or not all(isinstance(v, str) for v in found):
        raise InvalidReply("the reply's variations are not a list of strings")
    found = [v.strip() for v in found]
    if len(found) != n:
        raise InvalidReply(f"asked for {n} variations, got {len(found)}")
    low, high = _allowed_words(len(phrase.split()))
    wanted = Counter(phrases.slots(phrase))
    for v in found:
        if not v:
            raise InvalidReply("a variation is empty")
        if "\n" in v:
            raise InvalidReply(f"a variation is not one line: {v!r}")
        if v == phrase.strip():
            raise InvalidReply("a variation is the phrase itself")
        if Counter(phrases.slots(v)) != wanted or v.count("{") != sum(wanted.values()):
            raise InvalidReply(f"a variation does not keep the phrase's slots: {v!r}")
        if not low <= len(v.split()) <= high:
            raise InvalidReply(f"a variation has {len(v.split())} words, not {low} to {high}")
    if len(set(found)) != len(found):
        raise InvalidReply("a variation is given twice")
    return found


def _language(phrase_id: str) -> str:
    parts = phrase_id.split("#")[0].split(".")
    return next((LANGUAGES[p] for p in parts if p in LANGUAGES), DEFAULT_LANGUAGE)


@dataclass
class Result:
    sent: int = 0
    already_cached: int = 0
    failed: list[tuple[str, str]] = field(default_factory=list)


def run(profile_path: Path, client: Client, report: Callable[[str], None] = print) -> Result:
    """Send every bank phrase missing from the cache, caching each valid reply as it comes.

    The cache keeps only the bank's phrases, so a phrase removed from the bank leaves it too.
    """
    raw = profile.load(profile_path)
    bank_path, cache_path = phrases.paths(profile_path, raw)
    bank = phrases.load_bank(bank_path)
    cache = phrases.read_cache(cache_path, raw["text"]["model"])
    n = raw["text"]["variations_per_phrase"]
    in_bank = phrases.bank_phrases(bank)
    keys = {phrases.key(text) for _, text in in_bank}
    cache["phrases"] = {k: v for k, v in cache["phrases"].items() if k in keys}
    cache["model"] = client.model
    result = Result()
    for phrase_id, text in in_bank:
        if phrases.key(text) in cache["phrases"]:
            result.already_cached += 1
            continue
        about = bank[phrases.ABOUT][phrase_id.split(".")[0]]
        request = Request(text, about, _language(phrase_id), n)
        try:
            found = validate(text, client.variations(request), n)
        except InvalidReply as error:
            result.failed.append((phrase_id, str(error)))
            report(f"{phrase_id}: not cached, {error}")
            continue
        cache["phrases"][phrases.key(text)] = {
            "phrase": text,
            "variations": found,
            "model": client.model,
        }
        phrases.write_cache(cache_path, cache)
        result.sent += 1
    phrases.write_cache(cache_path, cache)
    return result
