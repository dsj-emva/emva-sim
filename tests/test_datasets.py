import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset, datasets, profile

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


def test_a_one_at_a_time_manifest_differs_from_the_middles_only_in_its_one_range(written):
    middle = manifest(written, "middle")["ranges"]
    assert {r["end"] for r in middle.values()} == {"middle"}
    raw = profile.load(PROFILE)
    for name in raw["sweep"]["one_at_a_time"]:
        for end in ("low", "high"):
            ranges = manifest(written, f"{name}@{end}")["ranges"]
            assert ranges.keys() == middle.keys()
            changed = {n for n in ranges if ranges[n] != middle[n]}
            assert changed == {name}, (name, end)
            assert ranges[name]["end"] == end


def test_the_extremes_put_every_range_swept_or_held_at_its_end(written):
    raw = profile.load(PROFILE)
    swept, held = raw["sweep"]["one_at_a_time"], raw["sweep"]["held_at_middle"]
    for end in ("low", "high"):
        ranges = manifest(written, f"all-{end}")["ranges"]
        assert ranges.keys() == set(swept) | set(held)
        assert {r["end"] for r in ranges.values()} == {end}


def test_a_manifest_carries_each_ranges_resolved_number(written):
    assert manifest(written, "middle")["ranges"]["volume.leads_per_month"]["value"] == 400
    assert manifest(written, "all-low")["ranges"]["volume.leads_per_month"]["value"] == 100
    referral = manifest(written, "effects.lead_source.referral@high")["ranges"]
    assert referral["effects.lead_source.referral"]["value"] == 6.0


def test_a_manifest_names_its_profile_its_dates_and_that_its_numbers_are_on_simulated_data(
    written,
):
    m = manifest(written, "middle")
    assert m["data_source"] == "on simulated data"
    assert m["profile"] == {
        "file": "planned-hospitality.toml",
        "sha256": hashlib.sha256(PROFILE.read_bytes()).hexdigest(),
    }
    assert m["history"] == {"start": "2024-01-01", "end": "2024-01-02"}
    assert m["export_date"] == "2024-03-01"


def test_each_manifest_carries_its_setting_and_seed(written):
    for setting in ["middle", "volume.leads_per_month@low", "all-high"]:
        m = manifest(written, setting)
        assert (m["setting"], m["seed"]) == (setting, datasets.seed(setting))
