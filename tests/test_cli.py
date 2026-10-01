import json
import subprocess
from datetime import date
from functools import partial
from pathlib import Path

import pytest

from emva_sim import cli, dataset, datasets

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
    folder = tmp_path / "middle"
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


def test_datasets_writes_every_dataset_of_the_sweep_and_labels_its_numbers(
    tmp_path, capsys, monkeypatch
):
    tiny = dataset.History(start=date(2024, 1, 1), end=date(2024, 1, 2), export=date(2024, 3, 1))
    monkeypatch.setattr(datasets, "write_all", partial(datasets.write_all, history=tiny))
    out = tmp_path / "datasets"
    cli.main(["datasets", "--profile", str(PROFILE), "--out", str(out)])
    assert len(json.loads((out / "index.json").read_text())["datasets"]) == 149
    printed = capsys.readouterr().out
    assert "149 datasets" in printed
    assert "on simulated data" in printed
    assert str(out) in printed


def test_the_project_script_runs():
    result = subprocess.run(["emva-sim", "--help"], capture_output=True, text=True, check=True)
    assert "generate" in result.stdout
