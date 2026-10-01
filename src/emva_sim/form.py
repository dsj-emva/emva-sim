"""The enquiry form as the profile describes it: fields by role, options by key or band."""

import math


def field(p: dict, role: str) -> dict:
    return next(f for f in p["form"]["fields"] if f["role"] == role)


def label(p: dict, role: str, key: str) -> str:
    return next(o["label"] for o in field(p, role)["options"] if o.get("key") == key)


def unsure(p: dict, role: str) -> str:
    return next(o["label"] for o in field(p, role)["options"] if o.get("not_sure"))


def band(p: dict, role: str, value: float) -> str:
    """The option whose band holds value: from its min (inclusive) to its max (exclusive)."""
    for option in field(p, role)["options"]:
        banded = "min" in option or "max" in option
        if banded and option.get("min", -math.inf) <= value < option.get("max", math.inf):
            return option["label"]
    raise ValueError(f"{value} is in no band of {role}")


def answer(p: dict, answers: dict[str, str], role: str) -> str:
    """A lead's answer to the field with this role."""
    return answers[field(p, role)["label"]]
