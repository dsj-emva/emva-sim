"""vary-phrases: have a language model rewrite each bank phrase once into natural variations.

Each phrase without a valid cached entry is sent once. The reply must pass phrases.check, and for
a phrase that carries a planted signal (the bank's [meaning]), each variation is put back to the
model with one question, whether it says what the phrase says; a variation answered "no" is
refused. Only a phrase whose reply passes everything is cached, so no made-up or drifted output
reaches generation (decision 0004). Generation reads the cache and never calls the model, so runs
stay reproducible from the seed.
"""

import json
import string
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import anthropic

from emva_sim import phrases, profile
from emva_sim.phrases import YES, InvalidVariations

KEY_NAME = "ANTHROPIC_API_KEY"
LANGUAGES = {"fr": "French"}
DEFAULT_LANGUAGE = "English"
NO = "no"

# string.Template, so braces in what the bank says about its text need no escaping.
SYSTEM = string.Template("""\
You write variations of one phrase for a generator of synthetic sales data.
The phrase is $about, written in $language.

Write $n variations of it, each as a real person might have written it instead. Rules:
- Keep the meaning exactly. Add no fact: no new number, name, place, date, amount, person or reason.
- Keep every placeholder in curly braces, such as {month}, exactly as written, as many times as it
  appears; write no other curly braces.
- Write in $language, in the same voice, and about as long as the phrase.
- Vary the wording freely: where a natural synonym or another construction exists, use it
  rather than repeating the phrase's key words.
- One line each, no numbering, no quotation marks around them.

Reply with JSON: {"variations": [...]}.""")

CHECK = string.Template("""\
You check one sentence for a generator of synthetic sales data.
Answer "yes" if the sentence says this, and "no" if it does not or is unclear: $statement.
Reply with JSON: {"answer": "yes"} or {"answer": "no"}.""")

VARIATIONS_SCHEMA = {
    "type": "object",
    "properties": {"variations": {"type": "array", "items": {"type": "string"}}},
    "required": ["variations"],
    "additionalProperties": False,
}
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": "string", "enum": [YES, NO]}},
    "required": ["answer"],
    "additionalProperties": False,
}


class NoApiKey(RuntimeError):
    pass


class ModelFailed(RuntimeError):
    """The model gave no usable reply: an API error, a refusal, or a reply cut short."""


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

    def answer(self, sentence: str, statement: str) -> str:
        """The model's reply: JSON saying whether the sentence says the statement."""


class HaikuClient:
    """Claude Haiku 4.5 through the Anthropic SDK."""

    def __init__(self, key: str, model: str):
        self.model = model
        self.client = anthropic.Anthropic(api_key=key)

    def variations(self, request: Request) -> str:
        system = SYSTEM.substitute(about=request.about, language=request.language, n=request.n)
        return self._ask(system, request.phrase, VARIATIONS_SCHEMA)

    def answer(self, sentence: str, statement: str) -> str:
        return self._ask(CHECK.substitute(statement=statement), sentence, ANSWER_SCHEMA)

    def _ask(self, system: str, content: str, schema: dict) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": content}],
                output_config={"format": {"type": "json_schema", "schema": schema}},
            )
        except anthropic.APIError as error:
            raise ModelFailed(f"the API failed: {type(error).__name__}") from error
        if response.stop_reason in ("max_tokens", "refusal"):
            raise ModelFailed(f"the reply stopped for {response.stop_reason}")
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


def _json(reply: str, name: str):
    try:
        return json.loads(reply)[name]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise InvalidVariations(f"the reply is not the asked JSON ({error})") from error


def validate(phrase: str, reply: str, n: int) -> list[str]:
    """The variations in the reply, if every rule of phrases.check holds."""
    return phrases.check(phrase, _json(reply, "variations"), n)


def _language(phrase_id: str) -> str:
    parts = phrase_id.split("#")[0].split(".")
    return next((LANGUAGES[p] for p in parts if p in LANGUAGES), DEFAULT_LANGUAGE)


@dataclass
class Result:
    sent: int = 0
    already_cached: int = 0
    failed: list[tuple[str, str]] = field(default_factory=list)


def _entry(client: Client, bank: dict, phrase: phrases.BankPhrase, n: int) -> dict:
    about = bank[phrases.ABOUT][phrase.id.split(".")[0]]
    request = Request(phrase.text, about, _language(phrase.id), n)
    found = validate(phrase.text, client.variations(request), n)
    entry = {"phrase": phrase.text, "variations": found, "model": client.model}
    said = phrases.meaning(bank, phrase.group)
    if said is not None:
        answers = [_json(client.answer(v, said), "answer") for v in found]
        drifted = [v for v, a in zip(found, answers, strict=True) if a != YES]
        if drifted:
            raise InvalidVariations(f"a variation does not say {said!r}: {drifted[0]!r}")
        entry["meaning_check"] = {"statement": said, "answers": answers}
    return entry


def run(profile_path: Path, client: Client, report: Callable[[str], None] = print) -> Result:
    """Send every bank phrase without a valid cached entry, caching each valid reply as it comes.

    An entry another model wrote, or one that no longer passes the checks, is sent again. The
    cache keeps only the bank's phrases, so a phrase removed from the bank leaves it too.
    """
    raw = profile.load(profile_path)
    bank_path, cache_path = phrases.paths(profile_path, raw)
    bank = phrases.load_bank(bank_path)
    cache = phrases.read_cache(cache_path, raw["text"]["model"])
    n = raw["text"]["variations_per_phrase"]
    in_bank = phrases.bank_phrases(bank)
    keys = {phrases.key(p.text) for p in in_bank}
    cache["phrases"] = {k: v for k, v in cache["phrases"].items() if k in keys}
    cache["model"] = client.model
    result = Result()
    for phrase in in_bank:
        known = cache["phrases"].get(phrases.key(phrase.text))
        try:
            phrases.check_entry(bank, phrase, known, client.model, n)
            result.already_cached += 1
            continue
        except InvalidVariations:
            pass
        try:
            entry = _entry(client, bank, phrase, n)
        except (InvalidVariations, ModelFailed) as error:
            result.failed.append((phrase.id, str(error)))
            report(f"{phrase.id}: not cached, {error}")
            continue
        cache["phrases"][phrases.key(phrase.text)] = entry
        phrases.write_cache(cache_path, cache)
        result.sent += 1
    phrases.write_cache(cache_path, cache)
    return result
