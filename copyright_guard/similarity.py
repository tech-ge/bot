"""Lightweight similarity checks (shingles + Jaccard)."""
from __future__ import annotations

import re
from typing import Iterable

_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def shingles(tokens: list[str], k: int = 5) -> set[tuple[str, ...]]:
    if len(tokens) < k:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def similarity(text_a: str, text_b: str, k: int = 5) -> float:
    return jaccard(shingles(_tokens(text_a), k), shingles(_tokens(text_b), k))


def max_similarity(text: str, corpus: Iterable[str], k: int = 5) -> float:
    t = shingles(_tokens(text), k)
    best = 0.0
    for other in corpus:
        score = jaccard(t, shingles(_tokens(other), k))
        if score > best:
            best = score
    return best
