import json
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset, datasets

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
TINY = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 2), export=date(2024, 3, 1))


@pytest.fixture(scope="module")
def written(tmp_path_factory):
    out = tmp_path_factory.mktemp("out") / "datasets"
    datasets.write_all(PROFILE, out, history=TINY)
    return out


def test_every_dataset_of_the_sweep_is_written_with_its_exports_hidden_truth_and_manifest(written):
    folders = sorted(p for p in written.iterdir() if p.is_dir())
    assert len(folders) == 1 + 2 * 73 + 2
    for folder in folders:
        assert {p.name for p in (folder / "export").iterdir()} == {
            "with-calls-and-notes",
            "deals-and-contacts-only",
        }
        assert (folder / "hidden-truth" / "hidden-truth.csv").exists()
        assert (folder / "manifest.json").exists()
