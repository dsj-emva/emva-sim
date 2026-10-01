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
import shutil
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from importlib.metadata import version
from pathlib import Path

from emva_sim import dataset, profile
from emva_sim.dataset import DEFAULT_HISTORY, History

BASE_SEED = 1
# The Data source, and the label every number from it carries.
DATA_SOURCE = {"data_source": "simulated data", "label": "on simulated data"}


def settings(raw: dict) -> list[str]:
    ends = [f"{name}@{end}" for name in raw["sweep"]["one_at_a_time"] for end in profile.ENDS]
    return ["middle", *ends, "all-low", "all-high"]


def seed(setting: str) -> int:
    return int(hashlib.sha256(f"{BASE_SEED}/{setting}".encode()).hexdigest()[:8], 16)


class NotAnEarlierOutput(ValueError):
    """The output folder holds something other than an earlier sweep, so it is not replaced."""


def write_all(profile_path: Path, out: Path, history: History = DEFAULT_HISTORY) -> list[dict]:
    """Write every dataset of the sweep and the index, and return the index's datasets.

    out ends holding exactly this sweep. It is built in "<out>.partial" beside it, which then
    replaces out, so a run that fails leaves an earlier output as it was. out and "<out>.partial"
    are replaced only when empty or holding an index.json of an earlier run.
    """
    out = Path(out)
    staging = out.with_name(out.name + ".partial")
    for folder in (out, staging):
        _check_replaceable(folder)
    profile_path = Path(profile_path)
    raw = profile.load(profile_path)
    named = {"file": profile_path.name, "sha256": _sha256(profile_path)}
    named_generator = {"version": version("emva-sim"), "sha256": _generator_sha256()}
    listed = [
        {"folder": dataset.folder_name(s), "setting": s, "seed": seed(s)} for s in settings(raw)
    ]
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    try:
        # The index goes in first, so an unfinished staging folder is known as this command's.
        _write_json(
            staging / "index.json",
            {**DATA_SOURCE, "profile": named, "base_seed": BASE_SEED, "datasets": listed},
        )
        with ProcessPoolExecutor() as pool:
            write_one = partial(_write_one, raw, named, named_generator, staging, history)
            list(pool.map(write_one, listed))
    except BaseException:
        shutil.rmtree(staging)
        raise
    shutil.rmtree(out, ignore_errors=True)
    staging.rename(out)
    return listed


def _check_replaceable(folder: Path) -> None:
    if folder.exists() and any(folder.iterdir()) and not (folder / "index.json").is_file():
        raise NotAnEarlierOutput(f"{folder} is not empty and holds no index.json of earlier output")


def _write_one(
    raw: dict, named: dict, generator: dict, out: Path, history: History, listed: dict
) -> None:
    """One dataset and its manifest, from its index entry; each depends only on its setting and
    seed, so they run in parallel."""
    folder = out / listed["folder"]
    dataset.write(raw, listed["setting"], listed["seed"], folder, history)
    _write_json(
        folder / "manifest.json",
        {
            **DATA_SOURCE,
            "profile": named,
            "generator": generator,
            "setting": listed["setting"],
            "seed": listed["seed"],
            "history": {"start": history.start.isoformat(), "end": history.end.isoformat()},
            "export_date": history.export.isoformat(),
            "ranges": _ranges(raw, listed["setting"]),
        },
    )


def _write_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _generator_sha256() -> str:
    """The SHA-256 of the generator's code: each of this package's .py files in name order, as
    its name, a NUL byte, its bytes and a NUL byte. Git-independent, so a dataset can be traced to
    the code that wrote it from any copy."""
    code = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        code.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return code.hexdigest()


def _sha256(path: Path) -> str:
    """The SHA-256 of the file's bytes, as `shasum -a 256` prints it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ranges(raw: dict, setting: str) -> dict[str, dict]:
    return {
        name: {"end": end, "value": profile.number(raw, name, end)}
        for name, end in profile.ends(raw, setting).items()
    }
