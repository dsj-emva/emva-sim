"""PreToolUse hook: keeps emva-sim sessions out of emva-app (decision 0007).

Only emva-app's CONTEXT.md, docs/adr/ and docs/START_HERE.md may be read; nothing in emva-app may be
written. It stops ordinary and accidental reads by file tools and shell commands, not deliberate
workarounds. Exit code 2 refuses the tool call and shows the reason to Claude.
"""

import json
import os
import re
import sys
from pathlib import Path

READ_TOOLS = {"Read", "Grep", "Glob"}
WRITE_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
ALLOWED_FILES = {Path("CONTEXT.md"), Path("docs/START_HERE.md")}
ALLOWED_FOLDER = Path("docs/adr")
GLOB_CHARACTERS = re.compile(r"[*?\[{]")
PATH_MENTION = re.compile(r"""[^\s'"`=:;,|&<>(){}]*emva-app[^\s'"`=:;,|&<>(){}]*""")


def resolve(raw: str, cwd: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    literal = GLOB_CHARACTERS.split(expanded, maxsplit=1)[0]
    return (cwd / literal).resolve()


def inside(path: Path, folder: Path) -> bool:
    return path == folder or folder in path.parents


def allowed(path: Path, emva_app: Path) -> bool:
    relative = path.relative_to(emva_app)
    return relative in ALLOWED_FILES or inside(relative, ALLOWED_FOLDER)


def paths_named(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name == "Bash":
        return PATH_MENTION.findall(tool_input.get("command", ""))
    keys = ("file_path", "notebook_path", "path", "pattern" if tool_name == "Glob" else None)
    return [tool_input[key] for key in keys if key and tool_input.get(key)]


def decide(tool_name: str, tool_input: dict, cwd: Path, emva_app: Path) -> str | None:
    """Return why the call is refused, or None when it may run."""
    emva_app = emva_app.resolve()
    cwd = cwd.resolve()
    if inside(cwd, emva_app):
        return "emva-sim sessions must not work inside emva-app (decision 0007)."
    base = cwd
    if tool_name == "Glob" and tool_input.get("path"):
        base = resolve(tool_input["path"], cwd)
    for raw in paths_named(tool_name, tool_input):
        path = resolve(raw, base if raw == tool_input.get("pattern") else cwd)
        if not inside(path, emva_app):
            continue
        if tool_name in WRITE_TOOLS:
            return f"emva-sim sessions never write to emva-app: {raw}"
        if not allowed(path, emva_app):
            return (
                f"emva-sim sessions may read only emva-app's CONTEXT.md, docs/adr/ and "
                f"docs/START_HERE.md (decision 0007); refused: {raw}"
            )
    return None


def main() -> None:
    call = json.load(sys.stdin)
    tool_name = call.get("tool_name", "")
    if tool_name not in READ_TOOLS | WRITE_TOOLS | {"Bash"}:
        return
    emva_app = Path(__file__).resolve().parents[2].parent / "emva-app"
    reason = decide(tool_name, call.get("tool_input", {}), Path(call.get("cwd", ".")), emva_app)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
