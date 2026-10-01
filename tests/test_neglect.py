"""Neglect: mostly the advertiser's behaviour, so good leads are neglected too, on simulated data.

The profile's rule: handling.neglect_follows_apparent_quality (f) of the decision follows how good a
lead looks at submission, neglecting it with a chance falling linearly from 2s for the worst-looking
lead to 0 for the best (s = handling.neglected_share; how a lead looks is its place among the leads
by the terms of effects visible at Submitted); the rest neglects any lead at s. Each test below
computes from that rule, the profile's numbers and each lead's terms what neglect should look like,
and checks the sample is within 3 standard errors of it.
"""

import math

from conftest import large_sample
from odds import log_odds

from emva_sim import ladder


def quality(row):
    """The hidden win log-odds without the handling's response-speed term."""
    return log_odds(row) - float(row["term_response_speed_by_quality"])


def apparent(p, row):
    seen = [n for n, e in p["effects"].items() if e["visible"] == ladder.SUBMITTED]
    return sum(float(row[f"term_{name}"]) for name in seen if f"term_{name}" in row)


def neglect_chances(sample):
    """Each lead's chance of being neglected under the profile's rule."""
    handling = sample.p["handling"]
    s, f = handling["neglected_share"], handling["neglect_follows_apparent_quality"]
    looks = [apparent(sample.p, row) for row in sample.rows]
    ordered = sorted(looks)
    n = len(looks)
    below = {}
    for i, value in enumerate(ordered):
        below.setdefault(value, [i, 0])[1] += 1
    places = [(below[v][0] + below[v][1] / 2) / n for v in looks]
    return [(1 - f) * s + f * min(1.0, 2 * s * (1 - place)) for place in places]


def is_neglected(row):
    return row["neglected_lead"] == "yes"


def test_good_leads_make_up_their_expected_share_of_the_neglected(middle_sample):
    # At the middle (s = 1%, f = 10%): the share of neglected leads that are in the top third
    # by hidden quality.
    chances = neglect_chances(middle_sample)
    top = [row["high_quality"] == "yes" for row in middle_sample.rows]
    expected = sum(c for c, good in zip(chances, top, strict=True) if good) / sum(chances)
    neglected = [
        good for row, good in zip(middle_sample.rows, top, strict=True) if is_neglected(row)
    ]
    found = sum(neglected) / len(neglected)
    se = math.sqrt(expected * (1 - expected) / len(neglected))
    assert abs(found - expected) <= 3 * se, (found, expected, se)


def test_high_quality_is_exactly_the_top_third_by_hidden_quality(middle_sample):
    # Ties at the edge are broken at random, so the group is a third exactly.
    rows = middle_sample.rows
    flagged = [quality(r) for r in rows if r["high_quality"] == "yes"]
    others = [quality(r) for r in rows if r["high_quality"] == "no"]
    assert len(flagged) == round(len(rows) / 3)
    # the hidden truth is written to about 6 decimals
    assert min(flagged) >= max(others) - 1e-5


def bottom_to_top(setting):
    """The log ratio of neglect rates, bottom third against top third by hidden quality: found,
    expected under the rule, and the standard error of the found one."""
    # Neglect raised to 20% of leads (from 0-2%) so the comparison has power; f is the setting's.
    sample = large_sample(setting, 1500, **{"handling.neglected_share": 0.2})
    chances = neglect_chances(sample)
    order = sorted(range(len(sample.rows)), key=lambda i: quality(sample.rows[i]))
    third = len(order) // 3
    bottom, top = order[:third], order[-third:]

    def rate(group):
        return sum(is_neglected(sample.rows[i]) for i in group) / len(group)

    def expected(group):
        return sum(chances[i] for i in group) / len(group)

    a, b = rate(bottom) * third, rate(top) * third
    return (
        math.log(rate(bottom) / rate(top)),
        math.log(expected(bottom) / expected(top)),
        math.sqrt(1 / a - 1 / third + 1 / b - 1 / third),
    )


def test_neglect_follows_how_a_lead_looks_more_at_the_high_end_than_at_the_low_end():
    low, low_expected, low_se = bottom_to_top("handling.neglect_follows_apparent_quality@low")
    high, high_expected, high_se = bottom_to_top("handling.neglect_follows_apparent_quality@high")
    # At the low end (f = 0) the rule expects no link at all; at the high end (f = 0.25) one.
    assert low_expected == 0.0
    assert abs(low - low_expected) <= 3 * low_se
    assert abs(high - high_expected) <= 3 * high_se
    assert high - low > 3 * math.hypot(low_se, high_se)
