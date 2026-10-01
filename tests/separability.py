"""Can one word or short phrase pick out the Leads carrying a planted text signal, or those
without it?

A rule is an n-gram of one to three words that a Lead's text contains, or lacks, read as saying
the Lead is in one class (carrying the signal, or not). Its precision is the share of the Leads it
picks that are in the class; its recall the share of the class it picks. A class with base rate b
is picked out when a rule with recall of at least MIN_RECALL reaches precision of at least
b + LIFT * (1 - b): half the way from guessing to certainty. A signal readable only from meaning
has no such rule, for either class.
"""

import re
from collections import Counter
from dataclasses import dataclass

WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)?")
MIN_RECALL = 0.10
LIFT = 0.5


def ngrams(text: str, longest: int = 3) -> set[tuple[str, ...]]:
    words = WORD.findall(text.lower())
    lengths = range(1, longest + 1)
    return {tuple(words[i : i + n]) for n in lengths for i in range(len(words) - n + 1)}


@dataclass(frozen=True)
class Rule:
    ngram: str
    contains: bool
    carrying: bool  # the class the rule picks out: the Leads carrying the signal, or the rest
    precision: float
    recall: float
    bound: float

    @property
    def separates(self) -> bool:
        return self.recall >= MIN_RECALL and self.precision >= self.bound

    @property
    def margin(self) -> float:
        """How far the rule's precision is below its bound (negative: it separates)."""
        return self.bound - self.precision if self.recall >= MIN_RECALL else 1.0


def rules(texts: list[tuple[str, bool]]) -> list[Rule]:
    """Every rule's precision and recall, for both classes, on (text, carries the signal)."""
    n = len(texts)
    in_class = {True: sum(flag for _, flag in texts)}
    in_class[False] = n - in_class[True]
    found = Counter()
    found_in = {True: Counter(), False: Counter()}
    for text, flag in texts:
        grams = ngrams(text)
        found.update(grams)
        found_in[flag].update(grams)
    every = []
    for carrying in (True, False):
        size = in_class[carrying]
        if not size:
            continue
        bound = size / n + LIFT * (1 - size / n)
        for gram, with_gram in found.items():
            hits = found_in[carrying][gram]
            name = " ".join(gram)
            every.append(Rule(name, True, carrying, hits / with_gram, hits / size, bound))
            if n - with_gram:
                missed = size - hits
                every.append(
                    Rule(name, False, carrying, missed / (n - with_gram), missed / size, bound)
                )
    return every


def strongest(texts: list[tuple[str, bool]]) -> Rule:
    return min(rules(texts), key=lambda r: r.margin)


def separating(texts: list[tuple[str, bool]]) -> list[Rule]:
    return [r for r in rules(texts) if r.separates]
