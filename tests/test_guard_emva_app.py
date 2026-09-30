import importlib.util
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "guard_emva_app.py"
spec = importlib.util.spec_from_file_location("guard_emva_app", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


@pytest.fixture
def workspace(tmp_path):
    app = tmp_path / "emva-app"
    (app / "docs" / "adr").mkdir(parents=True)
    (app / "services" / "api").mkdir(parents=True)
    (app / "CONTEXT.md").write_text("words")
    (app / "docs" / "START_HERE.md").write_text("plan")
    (app / "docs" / "adr" / "0007-ranges.md").write_text("decision")
    (app / "services" / "api" / "main.py").write_text("code")
    sim = tmp_path / "emva-sim"
    sim.mkdir()
    return sim, app


def refused(workspace, tool, tool_input):
    sim, app = workspace
    return guard.decide(tool, tool_input, sim, app) is not None


@pytest.mark.parametrize(
    "path",
    [
        "../emva-app/CONTEXT.md",
        "../emva-app/docs/START_HERE.md",
        "../emva-app/docs/adr/0007-ranges.md",
    ],
)
def test_read_of_an_allowed_file_passes(workspace, path):
    assert not refused(workspace, "Read", {"file_path": path})


def test_read_of_emva_app_code_is_refused(workspace):
    assert refused(workspace, "Read", {"file_path": "../emva-app/services/api/main.py"})


def test_read_by_absolute_path_is_refused(workspace):
    _, app = workspace
    assert refused(workspace, "Read", {"file_path": str(app / "services" / "api" / "main.py")})


def test_read_inside_emva_sim_passes(workspace):
    assert not refused(workspace, "Read", {"file_path": "CLAUDE.md"})


def test_grep_over_emva_app_services_is_refused(workspace):
    assert refused(workspace, "Grep", {"pattern": "def", "path": "../emva-app/services"})


def test_grep_over_the_decisions_passes(workspace):
    assert not refused(workspace, "Grep", {"pattern": "range", "path": "../emva-app/docs/adr"})


def test_grep_over_all_of_docs_is_refused(workspace):
    assert refused(workspace, "Grep", {"pattern": "x", "path": "../emva-app/docs"})


def test_glob_pattern_reaching_into_emva_app_is_refused(workspace):
    assert refused(workspace, "Glob", {"pattern": "../emva-app/**/*.py"})


def test_glob_over_the_decisions_passes(workspace):
    assert not refused(workspace, "Glob", {"pattern": "*.md", "path": "../emva-app/docs/adr"})


def test_writing_even_an_allowed_file_is_refused(workspace):
    assert refused(workspace, "Edit", {"file_path": "../emva-app/CONTEXT.md"})


@pytest.mark.parametrize(
    "command",
    [
        "cat ../emva-app/CONTEXT.md",
        "head -5 ../emva-app/docs/START_HERE.md",
        "cat ../emva-app/docs/adr/*.md",
        "wc -l ../emva-app/CONTEXT.md ../emva-app/docs/adr/0007-ranges.md",
    ],
)
def test_shell_command_on_allowed_files_passes(workspace, command):
    assert not refused(workspace, "Bash", {"command": command})


@pytest.mark.parametrize(
    "command",
    [
        "cat ../emva-app/services/api/main.py",
        "grep -r def ../emva-app/services",
        "ls ../emva-app",
        "cat ../emva-app/*",
        "cd ../emva-app && cat Makefile",
        "cat ../emva-app/CONTEXT.md ../emva-app/services/api/main.py",
        "cat '../emva-app/services/api/main.py'",
        "python -c 'open(\"../emva-app/services/api/main.py\")'",
    ],
)
def test_shell_command_touching_other_emva_app_files_is_refused(workspace, command):
    assert refused(workspace, "Bash", {"command": command})


def test_shell_command_by_absolute_path_is_refused(workspace):
    _, app = workspace
    assert refused(workspace, "Bash", {"command": f"cat {app}/services/api/main.py"})


def test_shell_command_naming_emva_app_only_as_a_word_passes(workspace):
    assert not refused(workspace, "Bash", {"command": 'git commit -m "no emva-app code read"'})


def test_any_tool_run_from_inside_emva_app_is_refused(workspace):
    sim, app = workspace
    assert guard.decide("Bash", {"command": "ls"}, app / "services", app) is not None


@pytest.mark.parametrize(
    "command",
    [
        "cd .. && cat emva-app/services/api/main.py",
        "cd ../emva-app/docs/adr && cat ../../services/api/main.py",
        "grep -rn def ..",
        "find .. -name '*.py'",
        "cat ../EMVA-APP/services/api/main.py",
    ],
)
def test_shell_command_reaching_emva_app_indirectly_is_refused(workspace, command):
    assert refused(workspace, "Bash", {"command": command})


@pytest.mark.parametrize(
    "command",
    [
        "rm ../emva-app/CONTEXT.md",
        "echo x > ../emva-app/docs/START_HERE.md",
        "echo x >> ../emva-app/docs/adr/0007-ranges.md",
        "sed -i '' 's/a/b/' ../emva-app/CONTEXT.md",
        "cp notes.md ../emva-app/docs/adr/0007-ranges.md",
    ],
)
def test_shell_command_writing_an_allowed_file_is_refused(workspace, command):
    assert refused(workspace, "Bash", {"command": command})


def test_reading_an_allowed_file_into_emva_sim_passes(workspace):
    assert not refused(workspace, "Bash", {"command": "cat ../emva-app/CONTEXT.md > words.md"})


def test_grep_over_the_parent_folder_is_refused(workspace):
    assert refused(workspace, "Grep", {"pattern": "def", "path": ".."})


def test_glob_over_the_parent_folder_is_refused(workspace):
    assert refused(workspace, "Glob", {"pattern": "../**/*.py"})


def test_read_with_different_letter_case_is_refused(workspace):
    assert refused(workspace, "Read", {"file_path": "../Emva-App/services/api/main.py"})


def test_refusal_names_every_readable_file(workspace):
    sim, app = workspace
    reason = guard.decide("Read", {"file_path": "../emva-app/services/api/main.py"}, sim, app)
    for readable in ("CONTEXT.md", "docs/adr/", "docs/START_HERE.md"):
        assert readable in reason


def run_hook(call):
    import json
    import subprocess
    import sys

    return subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(call), capture_output=True, text=True
    )


def test_hook_script_refuses_with_exit_code_2_next_to_the_real_emva_app():
    sim = HOOK.parents[2]
    call = {
        "tool_name": "Read",
        "tool_input": {"file_path": "../emva-app/services/api/main.py"},
        "cwd": str(sim),
    }
    result = run_hook(call)
    assert result.returncode == 2
    assert "CONTEXT.md" in result.stderr


def test_hook_script_lets_an_allowed_read_through():
    sim = HOOK.parents[2]
    call = {
        "tool_name": "Read",
        "tool_input": {"file_path": "../emva-app/CONTEXT.md"},
        "cwd": str(sim),
    }
    assert run_hook(call).returncode == 0
