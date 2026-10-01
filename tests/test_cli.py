import subprocess
from pathlib import Path

import pytest

from emva_sim import cli

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"


def test_generate_writes_a_dataset_and_labels_its_numbers(tmp_path, capsys):
    cli.main(
        [
            "generate",
            "--profile",
            str(PROFILE),
            "--setting",
            "middle",
            "--seed",
            "3",
            "--out",
            str(tmp_path),
        ]
    )
    folder = tmp_path / "planned-hospitality-middle-seed-3"
    assert (folder / "hidden-truth" / "hidden-truth.csv").exists()
    printed = capsys.readouterr().out
    assert "9600 leads" in printed
    assert "on simulated data" in printed
    assert str(folder) in printed


def test_an_unknown_setting_exits_with_an_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(
            ["generate", "--profile", str(PROFILE), "--setting", "nope", "--out", str(tmp_path)]
        )
    assert exit_info.value.code == 2
    assert "nope" in capsys.readouterr().err


def test_the_project_script_runs():
    result = subprocess.run(["emva-sim", "--help"], capture_output=True, text=True, check=True)
    assert "generate" in result.stdout
