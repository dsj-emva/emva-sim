"""Odds ratios of a won Outcome between two groups of contacted leads, from the hidden truth."""

import math
from collections import defaultdict


def log_odds(row) -> float:
    p = float(row["win_propensity"])
    return math.log(p / (1 - p))


# Strata are bins of this width on the log-odds. Response speed's term is continuous, so exact
# values would put each lead in a stratum of its own; within a bin the rest differs by at most
# 0.05, too little to move a measured odds ratio.
STRATUM_WIDTH = 0.05


def stratum(log_odds_value: float) -> int:
    return round(log_odds_value / STRATUM_WIDTH)


def rest_without(term):
    """A stratum key: the lead's log-odds without one term, so every other term is held fixed."""
    return lambda row: stratum(log_odds(row) - float(row[f"term_{term}"]))


def mantel_haenszel(rows, in_group, in_reference, stratum=lambda row: 0):
    """The log of the Mantel-Haenszel odds ratio of winning, group against reference, and its
    standard error (Robins, Breslow and Greenland), over contacted leads in strata."""
    cells = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        if row["neglected_lead"] == "yes":
            continue
        group, reference = in_group(row), in_reference(row)
        assert not (group and reference)
        if group or reference:
            won = row["outcome"] == "won"
            cells[stratum(row)][(0 if group else 2) + (0 if won else 1)] += 1
    r = s = pr = ps_qr = qs = 0.0
    for a, b, c, d in cells.values():
        n = a + b + c + d
        if not (a + b and c + d):
            continue
        ri, si, pi, qi = a * d / n, b * c / n, (a + d) / n, (b + c) / n
        r, s = r + ri, s + si
        pr, ps_qr, qs = pr + pi * ri, ps_qr + pi * si + qi * ri, qs + qi * si
    variance = pr / (2 * r * r) + ps_qr / (2 * r * s) + qs / (2 * s * s)
    return math.log(r / s), math.sqrt(variance)
