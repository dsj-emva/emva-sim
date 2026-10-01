import shutil
import subprocess

import pytest
from conftest import REAL_PROFILE

from emva_sim import cli, datasets


def test_generate_writes_a_dataset_and_labels_its_numbers(tmp_path, capsys, test_profile):
    cli.main(
        [
            "generate",
            "--profile",
            str(test_profile),
            "--setting",
            "middle",
            "--seed",
            "3",
            "--out",
            str(tmp_path),
        ]
    )
    folder = tmp_path / "middle"
    assert (folder / "hidden-truth" / "hidden-truth.csv").exists()
    printed = capsys.readouterr().out
    assert "9600 leads" in printed
    assert "on simulated data" in printed
    assert str(folder) in printed


def test_an_unknown_setting_exits_with_an_error(tmp_path, capsys, test_profile):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(
            ["generate", "--profile", str(test_profile), "--setting", "nope"]
            + ["--out", str(tmp_path)]
        )
    assert exit_info.value.code == 2
    assert "nope" in capsys.readouterr().err


def test_datasets_writes_the_sweep_of_the_profile_to_out_and_labels_its_numbers(
    tmp_path, capsys, monkeypatch
):
    called = []

    def write_all(profile_path, out):
        called.append((profile_path, out))
        return [{"folder": "middle"}, {"folder": "all-low"}]

    monkeypatch.setattr(datasets, "write_all", write_all)
    out = tmp_path / "datasets"
    cli.main(["datasets", "--profile", str(REAL_PROFILE), "--out", str(out)])
    assert called == [(REAL_PROFILE, out)]
    printed = capsys.readouterr().out
    assert "2 datasets" in printed
    assert "on simulated data" in printed
    assert str(out) in printed


def test_datasets_refuses_an_out_folder_that_is_not_an_earlier_output(tmp_path, capsys):
    (tmp_path / "precious.txt").write_text("keep me")
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["datasets", "--profile", str(REAL_PROFILE), "--out", str(tmp_path)])
    assert exit_info.value.code == 2
    assert "index.json" in capsys.readouterr().err
    assert (tmp_path / "precious.txt").read_text() == "keep me"


@pytest.mark.parametrize("command", ["generate", "datasets"])
def test_without_the_cached_variations_a_command_exits_naming_the_one_to_run(
    tmp_path, capsys, command
):
    for name in ("planned-hospitality.toml", "planned-hospitality.phrases.toml"):
        shutil.copy(REAL_PROFILE.parent / name, tmp_path / name)
    profile = tmp_path / "planned-hospitality.toml"
    with pytest.raises(SystemExit) as exit_info:
        cli.main([command, "--profile", str(profile), "--out", str(tmp_path / "out")])
    assert exit_info.value.code == 2
    assert "make vary-phrases" in capsys.readouterr().err


def test_the_project_script_runs():
    result = subprocess.run(["emva-sim", "--help"], capture_output=True, text=True, check=True)
    assert "generate" in result.stdout
