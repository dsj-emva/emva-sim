"""PreToolUse hook: keeps emva-sim sessions out of emva-app (decision 0007).

Only emva-app's CONTEXT.md, docs/adr/ and docs/START_HERE.md may be read; nothing in emva-app may be
written. It stops ordinary and accidental reads and writes by file tools and shell commands, not
deliberate workarounds. Exit code 2 refuses the tool call and shows the reason to Claude.
"""

import json
import os
import re
import sys
from pathlib import Path

READABLE_FILES = ("CONTEXT.md", "docs/START_HERE.md")
READABLE_FOLDERS = ("docs/adr",)
WRITE_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
GUARDED_TOOLS = WRITE_TOOLS | {"Read", "Grep", "Glob", "Bash"}

GLOB_CHARACTERS = re.compile(r"[*?\[{]")
SHELL_WORD = re.compile(r"""[^\s'"`=:;,|&<>(){}]+""")
SHELL_SEGMENT_BREAK = re.compile(r"&&|\|\||[;|&\n]")
CHANGE_DIRECTORY = re.compile(r"(?:^|[;&|(]\s*)(?:cd|pushd)\s+([^\s;&|)]+)")
REDIRECT_TARGET = re.compile(r">{1,2}\|?\s*([^\s;&|)]+)")
# Commands that change every path they name, and those that change only their last one.
WRITES_ALL_ARGUMENTS = {"rm", "rmdir", "touch", "tee", "truncate", "chmod", "chown", "unlink"}
WRITES_LAST_ARGUMENT = {"cp", "mv", "ln", "install", "rsync"}

READABLE_DESCRIPTION = ", ".join([*READABLE_FILES, *(f"{folder}/" for folder in READABLE_FOLDERS)])


def parts(path: Path | str) -> tuple[str, ...]:
    # macOS file names ignore case, so ../EMVA-APP is the same folder as ../emva-app.
    return tuple(part.casefold() for part in Path(path).parts)


READABLE_FILE_PARTS = {parts(f) for f in READABLE_FILES}
READABLE_FOLDER_PARTS = [parts(f) for f in READABLE_FOLDERS]


def resolve(raw: str, base: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    literal = GLOB_CHARACTERS.split(expanded, maxsplit=1)[0]
    return (base / literal).resolve()


def inside(path: Path, folder: Path) -> bool:
    return parts(path)[: len(parts(folder))] == parts(folder)


def is_readable(path: Path, emva_app: Path) -> bool:
    relative = parts(path)[len(parts(emva_app)) :]
    return relative in READABLE_FILE_PARTS or any(
        relative[: len(folder)] == folder for folder in READABLE_FOLDER_PARTS
    )


def read_refusal(path: Path, raw: str, emva_app: Path) -> str | None:
    if inside(path, emva_app):
        if is_readable(path, emva_app):
            return None
        return (
            f"emva-sim may read only {READABLE_DESCRIPTION} of emva-app (decision 0007); "
            f"refused: {raw}"
        )
    if inside(emva_app, path):
        return (
            f"{raw} contains emva-app, so searching or listing it would reach in (decision 0007)."
        )
    return None


def write_refusal(path: Path, raw: str, emva_app: Path) -> str | None:
    if inside(path, emva_app):
        return f"emva-sim never writes to emva-app (decision 0007); refused: {raw}"
    return None


def file_tool_paths(tool_name: str, tool_input: dict, cwd: Path) -> list[tuple[str, Path]]:
    """The paths a file tool names, each with the folder it is relative to."""
    keys = ("file_path", "notebook_path", "path")
    named = [(tool_input[key], cwd) for key in keys if tool_input.get(key)]
    if tool_name == "Glob" and tool_input.get("pattern"):
        base = resolve(tool_input["path"], cwd) if tool_input.get("path") else cwd
        named.append((tool_input["pattern"], base))
    return named


def shell_folders(command: str, cwd: Path) -> list[Path]:
    """The session folder plus every folder the command changes into."""
    folders = [cwd]
    for target in CHANGE_DIRECTORY.findall(command):
        folders += [resolve(target, folder) for folder in list(folders)]
    return folders


def shell_write_targets(command: str) -> list[str]:
    targets = REDIRECT_TARGET.findall(command)
    for segment in SHELL_SEGMENT_BREAK.split(command):
        words = SHELL_WORD.findall(segment)
        if not words:
            continue
        arguments = [word for word in words[1:] if not word.startswith("-")]
        if words[0] in WRITES_ALL_ARGUMENTS or (words[0] == "sed" and "-i" in words):
            targets += arguments
        elif words[0] in WRITES_LAST_ARGUMENT and arguments:
            targets.append(arguments[-1])
    return targets


def shell_refusal(command: str, cwd: Path, emva_app: Path) -> str | None:
    folders = shell_folders(command, cwd)
    for raw in shell_write_targets(command):
        for folder in folders:
            if reason := write_refusal(resolve(raw, folder), raw, emva_app):
                return reason
    for raw in SHELL_WORD.findall(command):
        for folder in folders:
            if reason := read_refusal(resolve(raw, folder), raw, emva_app):
                return reason
    return None


def decide(tool_name: str, tool_input: dict, cwd: Path, emva_app: Path) -> str | None:
    """Return why the call is refused, or None when it may run."""
    emva_app = emva_app.resolve()
    cwd = cwd.resolve()
    if inside(cwd, emva_app):
        return "emva-sim sessions must not work inside emva-app (decision 0007)."
    if tool_name == "Bash":
        return shell_refusal(tool_input.get("command", ""), cwd, emva_app)
    refusal = write_refusal if tool_name in WRITE_TOOLS else read_refusal
    for raw, base in file_tool_paths(tool_name, tool_input, cwd):
        if reason := refusal(resolve(raw, base), raw, emva_app):
            return reason
    return None


def main() -> None:
    call = json.load(sys.stdin)
    tool_name = call.get("tool_name", "")
    if tool_name not in GUARDED_TOOLS:
        return
    emva_app = Path(__file__).resolve().parents[3] / "emva-app"
    reason = decide(tool_name, call.get("tool_input", {}), Path(call.get("cwd", ".")), emva_app)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
