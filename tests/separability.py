"""Can one word or short phrase pick out the Leads carrying a planted text signal?

A rule is an n-gram of one to three words that the Lead's text contains, or lacks. Its precision
is the share of the Leads it picks that carry the signal; its recall the share of the Leads
carrying the signal that it picks. A signal readable only from meaning has no rule with both above
the bound.
"""

import re
from collections import Counter
from dataclasses import dataclass

WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)?")
BOUND = 0.8


def ngrams(text: str, longest: int = 3) -> set[tuple[str, ...]]:
    words = WORD.findall(text.lower())
    lengths = range(1, longest + 1)
    return {tuple(words[i : i + n]) for n in lengths for i in range(len(words) - n + 1)}


@dataclass(frozen=True)
class Rule:
    ngram: str
    contains: bool
    precision: float
    recall: float

    @property
    def strength(self) -> float:
        return min(self.precision, self.recall)


def rules(texts: list[tuple[str, bool]]) -> list[Rule]:
    """Every rule's precision and recall on (text, carries the signal) pairs."""
    carrying = sum(flag for _, flag in texts)
    found, found_carrying = Counter(), Counter()
    for text, flag in texts:
        grams = ngrams(text)
        found.update(grams)
        if flag:
            found_carrying.update(grams)
    every = []
    for gram, n in found.items():
        hits = found_carrying[gram]
        name = " ".join(gram)
        every.append(Rule(name, True, hits / n, hits / carrying))
        lacking = len(texts) - n
        if lacking:
            missed = carrying - hits
            every.append(Rule(name, False, missed / lacking, missed / carrying))
    return every


def strongest(texts: list[tuple[str, bool]]) -> Rule:
    return max(rules(texts), key=lambda r: r.strength)


def separating(texts: list[tuple[str, bool]]) -> list[Rule]:
    return [r for r in rules(texts) if r.precision > BOUND and r.recall > BOUND]
