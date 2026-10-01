"""Every dataset of a profile's sweep, each in its own folder named for its setting.

The sweep (decision 0007, and the profile's [sweep]): the middle; each range of
[sweep].one_at_a_time at its low and at its high, every other range at its middle; every range
low together; every range high together.

Seeds: each dataset's seed is the first 8 hex digits of the SHA-256 of "<BASE_SEED>/<setting>"
(`printf '1/middle' | shasum -a 256`), so it is the same on every run and platform, and adding or
removing a setting never changes another dataset's data.
"""

import hashlib
import json
from pathlib import Path

from emva_sim import dataset, profile
from emva_sim.dataset import DEFAULT_HISTORY, History

BASE_SEED = 1


def settings(raw: dict) -> list[str]:
    ends = [f"{name}@{end}" for name in raw["sweep"]["one_at_a_time"] for end in profile.ENDS]
    return ["middle", *ends, "all-low", "all-high"]


def seed(setting: str) -> int:
    return int(hashlib.sha256(f"{BASE_SEED}/{setting}".encode()).hexdigest()[:8], 16)


def folder_name(setting: str) -> str:
    """The setting, with "<range name>@<end>" written as the profile key its number is read from."""
    return setting.replace("@", ".")


def write_all(profile_path: Path, out: Path, history: History = DEFAULT_HISTORY) -> None:
    profile_path = Path(profile_path)
    raw = profile.load(profile_path)
    named = {"file": profile_path.name, "sha256": _sha256(profile_path)}
    for setting in settings(raw):
        folder = Path(out) / folder_name(setting)
        dataset.write(raw, setting, seed(setting), folder, history)
        m = {
            "data_source": "on simulated data",
            "profile": named,
            "setting": setting,
            "seed": seed(setting),
            "history": {"start": history.start.isoformat(), "end": history.end.isoformat()},
            "export_date": history.export.isoformat(),
            "ranges": _ranges(raw, setting),
        }
        (folder / "manifest.json").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    """The SHA-256 of the file's bytes, as `shasum -a 256` prints it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ranges(raw: dict, setting: str) -> dict[str, dict]:
    ranges = {}
    for name, end in profile.ends(raw, setting).items():
        node = raw
        for key in name.split("."):
            node = node[key]
        ranges[name] = {"end": end, "value": node[end]}
    return ranges
