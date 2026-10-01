"""Neglect: mostly the advertiser's behaviour, so good leads are neglected too, on simulated data.

handling.neglect_follows_apparent_quality (f) is the share of the neglect decision that follows how
good a lead looks at submission; the rest neglects any lead at handling.neglected_share (s). If
neglect followed exactly the hidden quality, the top third would be neglected at s x (1 - 2f/3)
(a lead's chance falling linearly from 2s at the worst-looking to 0 at the best); how a lead looks
is only part of its quality, so the top third's rate lies between that and s.
"""

import math

from conftest import large_sample


def quality(row):
    """The hidden win log-odds without the handling's response-speed term."""
    p = float(row["win_propensity"])
    return math.log(p / (1 - p)) - float(row["term_response_speed_by_quality"])


def thirds(rows):
    ordered = sorted(quality(r) for r in rows)
    low, high = ordered[len(ordered) // 3], ordered[2 * len(ordered) // 3]
    bottom = [r for r in rows if quality(r) < low]
    top = [r for r in rows if quality(r) >= high]
    return bottom, top


def neglected(rows):
    return sum(r["neglected_lead"] == "yes" for r in rows)


def test_good_leads_are_neglected_at_about_the_profiles_rate(middle_sample):
    s, f = 0.01, 0.10
    _, top = thirds(middle_sample)
    rate = neglected(top) / len(top)
    se = math.sqrt(s / len(top))
    assert s * (1 - 2 * f / 3) - 3 * se <= rate <= s + 3 * se
    assert neglected(top) > 300


def test_high_quality_is_exactly_the_top_third_by_hidden_quality(middle_sample):
    # Ties at the edge are broken at random, so the group is a third exactly.
    flagged = [quality(r) for r in middle_sample if r["high_quality"] == "yes"]
    others = [quality(r) for r in middle_sample if r["high_quality"] == "no"]
    assert len(flagged) == round(len(middle_sample) / 3)
    # the hidden truth is written to about 6 decimals
    assert min(flagged) >= max(others) - 1e-5


def log_ratio_bottom_to_top(setting):
    # Neglect raised to 20% of leads (from 0-2%) so the comparison has power; f is the setting's.
    rows = large_sample(setting, 1500, **{"handling.neglected_share": 0.2})
    bottom, top = thirds(rows)
    a, b = neglected(bottom), neglected(top)
    log_ratio = math.log(a / len(bottom)) - math.log(b / len(top))
    return log_ratio, math.sqrt(1 / a + 1 / b)


def test_neglect_follows_how_a_lead_looks_more_at_the_high_end_than_at_the_low_end():
    low, low_se = log_ratio_bottom_to_top("handling.neglect_follows_apparent_quality@low")
    high, high_se = log_ratio_bottom_to_top("handling.neglect_follows_apparent_quality@high")
    # At the low end (f = 0) neglect is independent of quality: the ratio is 1.
    assert abs(low) < 3 * low_se
    # At the high end (f = 0.25) the worst third is neglected more than the best.
    assert high - low > 3 * math.hypot(low_se, high_se)
    assert high > math.log(1.1)
