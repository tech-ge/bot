"""Simple lexicon-based sentiment (no external calls)."""
from __future__ import annotations

import re
from dataclasses import dataclass

_POS = {"good","great","awesome","love","like","nice","happy","excellent","win",
        "amazing","fantastic","cool","best","perfect","thanks","thank","yes"}
_NEG = {"bad","terrible","awful","hate","dislike","sad","angry","worst","fail",
        "broken","poor","no","nope","never","problem","issue"}

_WORD = re.compile(r"[A-Za-z']+")


@dataclass
class Sentiment:
    score: float
    label: str


def analyze(text: str) -> Sentiment:
    words = [w.lower() for w in _WORD.findall(text or "")]
    if not words:
        return Sentiment(0.0, "neutral")
    pos = sum(1 for w in words if w in _POS)
    neg = sum(1 for w in words if w in _NEG)
    total = pos + neg
    if total == 0:
        return Sentiment(0.0, "neutral")
    score = (pos - neg) / total
    label = "positive" if score > 0.15 else "negative" if score < -0.15 else "neutral"
    return Sentiment(score, label)
