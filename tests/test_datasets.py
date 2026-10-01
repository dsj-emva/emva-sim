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


def manifest(written, setting):
    return json.loads((written / datasets.folder_name(setting) / "manifest.json").read_text())


@pytest.mark.parametrize(
    ("setting", "folder"),
    [
        ("middle", "middle"),
        ("all-low", "all-low"),
        ("volume.leads_per_month@low", "volume.leads_per_month.low"),
        ("effects.lead_source.referral@high", "effects.lead_source.referral.high"),
    ],
)
def test_a_folder_is_named_for_its_setting_by_the_profile_key_its_range_is_read_from(
    setting, folder
):
    assert datasets.folder_name(setting) == folder


def test_each_seed_is_the_sha256_of_the_base_seed_and_the_setting_so_others_never_shift():
    # The first 8 hex digits of: printf '1/middle' | shasum -a 256, and so on.
    assert datasets.BASE_SEED == 1
    assert datasets.seed("middle") == 0xE95D4948
    assert datasets.seed("volume.leads_per_month@low") == 0xB0EB7AC6


def test_each_manifest_carries_its_setting_and_seed(written):
    for setting in ["middle", "volume.leads_per_month@low", "all-high"]:
        m = manifest(written, setting)
        assert (m["setting"], m["seed"]) == (setting, datasets.seed(setting))
