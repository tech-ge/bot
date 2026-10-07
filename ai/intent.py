"""Rule-based intent classifier for inbound messages."""
from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("greeting", re.compile(r"\b(hi|hello|hey|yo|good morning|good evening)\b", re.I)),
    ("question", re.compile(r"\?$|^(what|how|why|when|where|who|can you|could you)\b", re.I)),
    ("support",  re.compile(r"\b(help|issue|problem|broken|error|bug|support)\b", re.I)),
    ("pricing",  re.compile(r"\b(price|pricing|cost|how much|quote)\b", re.I)),
    ("praise",   re.compile(r"\b(love|great|awesome|amazing|thanks|thank you)\b", re.I)),
    ("complaint",re.compile(r"\b(angry|refund|cancel|worst|terrible|disappointed)\b", re.I)),
    ("spam",     re.compile(r"\b(free|click here|subscribe|giveaway|dm me|crypto)\b", re.I)),
]


@dataclass
class Intent:
    name: str
    confidence: float


def classify(text: str) -> Intent:
    t = (text or "").strip()
    if not t:
        return Intent("unknown", 0.0)
    for name, pat in _PATTERNS:
        if pat.search(t):
            return Intent(name, 0.75)
    return Intent("other", 0.4)
