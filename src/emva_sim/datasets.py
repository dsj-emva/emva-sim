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
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

from emva_sim import dataset, profile
from emva_sim.dataset import DEFAULT_HISTORY, History

BASE_SEED = 1
DATA_SOURCE = "on simulated data"


def settings(raw: dict) -> list[str]:
    ends = [f"{name}@{end}" for name in raw["sweep"]["one_at_a_time"] for end in profile.ENDS]
    return ["middle", *ends, "all-low", "all-high"]


def seed(setting: str) -> int:
    return int(hashlib.sha256(f"{BASE_SEED}/{setting}".encode()).hexdigest()[:8], 16)


def folder_name(setting: str) -> str:
    """The setting, with "<range name>@<end>" written as the profile key its number is read from."""
    return setting.replace("@", ".")


def write_all(profile_path: Path, out: Path, history: History = DEFAULT_HISTORY) -> list[dict]:
    """Write every dataset of the sweep and the index, and return the index's datasets."""
    profile_path = Path(profile_path)
    raw = profile.load(profile_path)
    named = {"file": profile_path.name, "sha256": _sha256(profile_path)}
    swept = settings(raw)
    with ProcessPoolExecutor() as pool:
        list(pool.map(partial(_write_one, raw, named, Path(out), history), swept))
    listed = [{"folder": folder_name(s), "setting": s, "seed": seed(s)} for s in swept]
    _write_json(
        Path(out) / "index.json",
        {"data_source": DATA_SOURCE, "profile": named, "base_seed": BASE_SEED, "datasets": listed},
    )
    return listed


def _write_one(raw: dict, named: dict, out: Path, history: History, setting: str) -> None:
    """One dataset and its manifest; each depends only on its setting, so they run in parallel."""
    folder = out / folder_name(setting)
    dataset.write(raw, setting, seed(setting), folder, history)
    _write_json(
        folder / "manifest.json",
        {
            "data_source": DATA_SOURCE,
            "profile": named,
            "setting": setting,
            "seed": seed(setting),
            "history": {"start": history.start.isoformat(), "end": history.end.isoformat()},
            "export_date": history.export.isoformat(),
            "ranges": _ranges(raw, setting),
        },
    )


def _write_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    """The SHA-256 of the file's bytes, as `shasum -a 256` prints it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ranges(raw: dict, setting: str) -> dict[str, dict]:
    return {
        name: {"end": end, "value": profile.number(raw, name, end)}
        for name, end in profile.ends(raw, setting).items()
    }
