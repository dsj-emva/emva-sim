"""A stand-in for the model that varies phrases, so no test touches the network.

Its variations are the phrase with its first letter's case and its closing punctuation changed: they
pass vary.validate, keep every word and slot, and add no word of their own, so whatever the tests
measure on text built from them is what the phrase bank itself says.
"""

import json
import shutil
import tempfile
from pathlib import Path

from emva_sim import vary

ENDINGS = ["", ".", "!", "...", "!!", "?"]


def variations(phrase: str, n: int) -> list[str]:
    stem = phrase.rstrip(".!?")
    cases = [stem, stem[:1].swapcase() + stem[1:]]
    found = []
    for case in cases:
        for ending in ENDINGS:
            candidate = case + ending
            if candidate != phrase and candidate not in found and candidate.strip():
                found.append(candidate)
    return found[:n]


class Echo:
    model = "echo"

    def variations(self, request: vary.Request) -> str:
        return json.dumps({"variations": variations(request.phrase, request.n)})


def profile_with_echoed_variations(profile: Path) -> Path:
    """A copy of the profile and its phrase bank in a temporary folder, with a cache written by
    Echo through vary-phrases itself."""
    folder = Path(tempfile.mkdtemp(prefix="emva-sim-test-profile-"))
    raw = vary.profile.load(profile)
    shutil.copy(profile, folder / profile.name)
    shutil.copy(profile.parent / raw["text"]["phrase_bank"], folder / raw["text"]["phrase_bank"])
    copy = folder / profile.name
    result = vary.run(copy, Echo(), report=lambda line: None)
    if result.failed:
        raise AssertionError(f"the echoed variations break vary's rules: {result.failed[:3]}")
    return copy
