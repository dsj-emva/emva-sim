import hashlib
import json
import shutil
import tomllib
from datetime import date
from pathlib import Path

import pytest
from conftest import PROFILE

from emva_sim import dataset, datasets, profile

TINY = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 2), export=date(2024, 3, 1))


@pytest.fixture(scope="module")
def written(tmp_path_factory):
    out = tmp_path_factory.mktemp("out") / "datasets"
    datasets.write_all(PROFILE, out, history=TINY)
    return out


def sweep_size():
    """The middle, each one-at-a-time range at its low and its high, and the two extremes."""
    return 1 + 2 * len(profile.load(PROFILE)["sweep"]["one_at_a_time"]) + 2


def test_the_planned_hospitality_sweep_is_149_datasets_as_the_user_ruled():
    assert len(datasets.settings(profile.load(PROFILE))) == sweep_size() == 149


def test_every_dataset_of_the_sweep_is_written_with_its_exports_hidden_truth_and_manifest(written):
    folders = sorted(p for p in written.iterdir() if p.is_dir())
    assert len(folders) == sweep_size()
    for folder in folders:
        assert {p.name for p in (folder / "export").iterdir()} == {
            "with-calls-and-notes",
            "deals-and-contacts-only",
        }
        truth = (folder / "hidden-truth" / "hidden-truth.csv").read_text().splitlines()
        assert len(truth) > 1, folder.name
        assert (folder / "manifest.json").exists()


def manifest(written, setting):
    return json.loads((written / dataset.folder_name(setting) / "manifest.json").read_text())


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
    assert dataset.folder_name(setting) == folder


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
    assert (m["data_source"], m["label"]) == ("simulated data", "on simulated data")
    assert m["profile"] == {
        "file": "planned-hospitality.toml",
        "sha256": hashlib.sha256(PROFILE.read_bytes()).hexdigest(),
    }
    assert m["history"] == {"start": "2024-01-01", "end": "2024-01-02"}
    assert m["export_date"] == "2024-03-01"


def test_a_manifest_names_the_phrase_bank_and_the_cached_variations_its_text_came_from(written):
    folder = PROFILE.parent
    assert manifest(written, "middle")["phrases"] == {
        name: {"file": file, "sha256": hashlib.sha256((folder / file).read_bytes()).hexdigest()}
        for name, file in [
            ("bank", "planned-hospitality.phrases.toml"),
            ("variations", "planned-hospitality.variations.json"),
        ]
    }


def test_a_manifest_names_the_generator_that_wrote_it_by_version_and_code_hash(written):
    src = Path(__file__).parent.parent / "src" / "emva_sim"
    code = hashlib.sha256()
    for path in sorted(src.glob("*.py")):
        code.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    pyproject = tomllib.loads((src.parent.parent / "pyproject.toml").read_text())
    assert manifest(written, "middle")["generator"] == {
        "version": pyproject["project"]["version"],
        "sha256": code.hexdigest(),
    }


def test_the_index_lists_every_dataset_its_setting_and_its_seed(written):
    index = json.loads((written / "index.json").read_text())
    assert (index["data_source"], index["label"]) == ("simulated data", "on simulated data")
    assert index["base_seed"] == 1
    listed = index["datasets"]
    assert len(listed) == sweep_size()
    assert listed[0] == {"folder": "middle", "setting": "middle", "seed": 0xE95D4948}
    assert {d["folder"] for d in listed} == {p.name for p in written.iterdir() if p.is_dir()}
    for d in listed:
        assert manifest(written, d["setting"])["seed"] == d["seed"]


def files(folder):
    return {p.relative_to(folder): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def test_writing_twice_gives_byte_identical_output(written, tmp_path):
    datasets.write_all(PROFILE, tmp_path, history=TINY)
    assert files(tmp_path) == files(written)


def test_a_dataset_is_the_one_its_seed_generates_alone(written, tmp_path):
    setting = "volume.leads_per_month@high"
    alone = dataset.generate(PROFILE, setting, datasets.seed(setting), tmp_path, history=TINY)
    swept = files(written / dataset.folder_name(setting))
    del swept[Path("manifest.json")]
    assert swept == files(alone)


def test_a_run_leaves_exactly_the_current_sweep_removing_folders_of_earlier_settings(
    written, tmp_path
):
    out = tmp_path / "datasets"
    datasets.write_all(PROFILE, out, history=TINY)
    (out / "dropped.range.low").mkdir()
    (out / "dropped.range.low" / "manifest.json").write_text("{}")
    datasets.write_all(PROFILE, out, history=TINY)
    assert files(out) == files(written)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["datasets"]


def test_a_non_empty_folder_without_an_index_is_refused_and_left_untouched(tmp_path):
    out = tmp_path / "home"
    out.mkdir()
    (out / "precious.txt").write_text("keep me")
    with pytest.raises(datasets.NotAnEarlierOutput):
        datasets.write_all(PROFILE, out, history=TINY)
    assert files(out) == {Path("precious.txt"): b"keep me"}
    assert sorted(p.name for p in tmp_path.iterdir()) == ["home"]


def test_a_crash_mid_run_leaves_the_earlier_output_intact(written, tmp_path):
    out = tmp_path / "datasets"
    datasets.write_all(PROFILE, out, history=TINY)
    # A copy of the profile, beside its phrase bank and cache, with a range made unreadable.
    shutil.copytree(PROFILE.parent, tmp_path / "broken")
    broken = tmp_path / "broken" / PROFILE.name
    text = PROFILE.read_text()
    leads_per_month = "[volume.leads_per_month]\nlow = 100\nmiddle = 400\nhigh = 1000\n"
    assert leads_per_month in text
    broken.write_text(text.replace(leads_per_month, leads_per_month.replace("1000", '"boom"')))
    with pytest.raises(TypeError):
        datasets.write_all(broken, out, history=TINY)
    assert files(out) == files(written)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["broken", "datasets"]


def test_each_manifest_carries_its_setting_and_seed(written):
    for setting in ["middle", "volume.leads_per_month@low", "all-high"]:
        m = manifest(written, setting)
        assert (m["setting"], m["seed"]) == (setting, datasets.seed(setting))
