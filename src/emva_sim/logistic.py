"""Between a chance and its log-odds."""

import math


def logit(chance: float) -> float:
    return math.log(chance / (1 - chance))


def sigmoid(log_odds: float) -> float:
    return 1 / (1 + math.exp(-log_odds))
