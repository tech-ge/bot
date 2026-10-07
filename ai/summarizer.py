"""Extractive summarizer (frequency-based)."""
from __future__ import annotations

import re
from collections import Counter

_SENT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z']+")

STOP = {
    "the","a","an","and","or","but","if","then","so","of","to","in","on","at",
    "for","with","by","is","are","was","were","be","been","being","this","that",
    "it","as","from","i","you","we","they","he","she","them","us","our","your",
    "his","her","its","not","no","do","does","did","have","has","had","will",
    "would","can","could","should","may","might","must","just","very","also",
}


def summarize(text: str, max_sentences: int = 3) -> str:
    sents = [s.strip() for s in _SENT.split(text or "") if s.strip()]
    if len(sents) <= max_sentences:
        return " ".join(sents)

    words = [w.lower() for w in _WORD.findall(text)]
    freq = Counter(w for w in words if w not in STOP and len(w) > 2)
    if not freq:
        return " ".join(sents[:max_sentences])

    scored: list[tuple[float, int, str]] = []
    for idx, s in enumerate(sents):
        ws = [w.lower() for w in _WORD.findall(s)]
        if not ws:
            continue
        score = sum(freq[w] for w in ws if w in freq) / len(ws)
        scored.append((score, idx, s))

    scored.sort(reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[1])
    return " ".join(s for _, _, s in top)
