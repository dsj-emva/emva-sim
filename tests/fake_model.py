"""The one stand-in for the model that varies phrases, so no test touches the network.

By default its variations are the phrase with its first letter's case and its closing punctuation
changed, which pass every rule, keep every word and slot and add no word of their own, so what the
tests measure on text built from them is what the phrase bank itself says; and it answers "yes"
to every meaning check. Tests give it other answers to see them refused.
"""

import json
import shutil
from collections.abc import Callable
from pathlib import Path

from emva_sim import profile, vary

ENDINGS = ["", ".", "!", "...", "!!", "?"]
MODEL = "fake-model"


def echoed(phrase: str, n: int) -> list[str]:
    stem = phrase.rstrip(".!?")
    found = []
    for case in (stem, stem[:1].swapcase() + stem[1:]):
        for ending in ENDINGS:
            candidate = case + ending
            if candidate != phrase and candidate not in found and candidate.strip():
                found.append(candidate)
    return found[:n]


class FakeModel:
    """Answers as the model would, recording what it was asked."""

    model = MODEL

    def __init__(
        self,
        variations: Callable[[vary.Request], list[str]] | None = None,
        says: Callable[[str, str], bool] | None = None,
        reply: Callable[[vary.Request], str] | None = None,
    ):
        self.asked: list[vary.Request] = []
        self.checked: list[tuple[str, str]] = []
        self._variations = variations or (lambda r: echoed(r.phrase, r.n))
        self._says = says or (lambda sentence, statement: True)
        self._reply = reply

    def variations(self, request: vary.Request) -> str:
        self.asked.append(request)
        if self._reply:
            return self._reply(request)
        return json.dumps({"variations": self._variations(request)})

    def answer(self, sentence: str, statement: str) -> str:
        self.checked.append((sentence, statement))
        return json.dumps({"answer": "yes" if self._says(sentence, statement) else "no"})


def profile_with_fake_variations(real: Path, folder: Path) -> Path:
    """A copy of the profile, naming the fake model, and its phrase bank in folder, with a cache
    the fake model wrote through vary-phrases itself."""
    raw = profile.load(real)
    text = real.read_text(encoding="utf-8")
    named = f'model = "{raw["text"]["model"]}"'
    assert named in text
    copy = folder / real.name
    copy.write_text(text.replace(named, f'model = "{MODEL}"'), encoding="utf-8")
    shutil.copy(real.parent / raw["text"]["phrase_bank"], folder / raw["text"]["phrase_bank"])
    result = vary.run(copy, FakeModel(), report=lambda line: None)
    if result.failed:
        raise AssertionError(f"the fake variations break vary's rules: {result.failed[:3]}")
    return copy
