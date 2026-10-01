"""Load an Industry profile and resolve every range to one number for a named setting.

A range is a table with low, middle and high. Its name is its dotted path, as used in the
profile's [sweep]. Settings: "middle"; "<range name>@low" or "<range name>@high" (that range at
its end, every other range at its middle); "all-low"; "all-high".
"""

import tomllib
from pathlib import Path

ENDS = ("low", "high")


class UnknownSetting(ValueError):
    pass


def load(path: Path) -> dict:
    return tomllib.loads(Path(path).read_text())


def _is_range(node) -> bool:
    return isinstance(node, dict) and {"low", "middle", "high"} <= node.keys()


def range_names(raw: dict) -> list[str]:
    names = []

    def walk(node, path):
        if _is_range(node):
            names.append(".".join(path))
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, (*path, key))

    walk(raw, ())
    return names


def _ends(raw: dict, setting: str) -> tuple[str, dict[str, str]]:
    if setting == "middle":
        return "middle", {}
    if setting in ("all-low", "all-high"):
        return setting.removeprefix("all-"), {}
    name, _, end = setting.rpartition("@")
    if end not in ENDS or name not in range_names(raw):
        raise UnknownSetting(setting)
    return "middle", {name: end}


def ends(raw: dict, setting: str) -> dict[str, str]:
    """The end ("low", "middle" or "high") each range is at in the setting, by range name."""
    default, exceptions = _ends(raw, setting)
    return {name: exceptions.get(name, default) for name in range_names(raw)}


def resolve(raw: dict, setting: str) -> dict:
    end_of = ends(raw, setting)

    def walk(node, path):
        if _is_range(node):
            return node[end_of[".".join(path)]]
        if isinstance(node, dict):
            return {key: walk(value, (*path, key)) for key, value in node.items()}
        return node

    return walk(raw, ())
