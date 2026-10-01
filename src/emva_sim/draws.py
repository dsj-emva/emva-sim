"""Random draws the generator needs, all from one explicit random.Random."""

import math
from random import Random
from statistics import NormalDist

_NORMAL = NormalDist()
_EDGE = 1e-12


def poisson(rng: Random, mean: float) -> int:
    limit, k, product = math.exp(-mean), 0, rng.random()
    while product > limit:
        k += 1
        product *= rng.random()
    return k


def lognormal(rng: Random, median: float, sigma: float) -> float:
    return median * math.exp(sigma * rng.gauss(0.0, 1.0))


def lognormal_between(rng: Random, median: float, sigma: float, low: float, high: float) -> float:
    """A lognormal draw conditioned on falling between low (0 or more) and high."""

    def cdf(x):
        return _NORMAL.cdf(math.log(x / median) / sigma) if x > 0 else 0.0

    u = cdf(low) + (cdf(high) - cdf(low)) * rng.random()
    return median * math.exp(sigma * _NORMAL.inv_cdf(min(max(u, _EDGE), 1 - _EDGE)))


def sigma_from_share_above(median: float, threshold: float, share_above: float) -> float:
    """The lognormal sigma with this median that puts share_above of draws above threshold."""
    z = _NORMAL.inv_cdf(1 - share_above) if 0 < share_above < 1 else 0.0
    sigma = math.log(threshold / median) / z if z else 0.0
    if not sigma > 0:
        raise ValueError(
            f"a median of {median} cannot have {share_above:.0%} of draws above {threshold}"
        )
    return sigma


def sorted_uniforms(rng: Random, n: int, low: float, high: float) -> list[float]:
    return sorted(low + (high - low) * rng.random() for _ in range(n))
