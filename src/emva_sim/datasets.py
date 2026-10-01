"""Every dataset of a profile's sweep, each in its own folder named for its setting.

The sweep (decision 0007, and the profile's [sweep]): the middle; each range of
[sweep].one_at_a_time at its low and at its high, every other range at its middle; every range
low together; every range high together.
"""

import json
from pathlib import Path

from emva_sim import dataset, profile
from emva_sim.dataset import DEFAULT_HISTORY, History


def settings(raw: dict) -> list[str]:
    ends = [f"{name}@{end}" for name in raw["sweep"]["one_at_a_time"] for end in profile.ENDS]
    return ["middle", *ends, "all-low", "all-high"]


def write_all(profile_path: Path, out: Path, history: History = DEFAULT_HISTORY) -> None:
    raw = profile.load(profile_path)
    for setting in settings(raw):
        folder = Path(out) / setting
        dataset.write(raw, setting, 1, folder, history)
        (folder / "manifest.json").write_text(json.dumps({"setting": setting}))
