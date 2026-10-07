"""Caption + hashtag helpers."""
from __future__ import annotations

import re
from typing import Iterable

_HASHTAG_RE = re.compile(r"#\w+")


def extract_hashtags(text: str) -> list[str]:
    return _HASHTAG_RE.findall(text or "")


def ensure_hashtags(text: str, tags: Iterable[str], max_tags: int = 15) -> str:
    existing = set(extract_hashtags(text))
    to_add: list[str] = []
    for tag in tags:
        t = tag if tag.startswith("#") else f"#{tag}"
        t = re.sub(r"\s+", "", t)
        if t.lower() not in {e.lower() for e in existing}:
            to_add.append(t)
        if len(existing) + len(to_add) >= max_tags:
            break
    if not to_add:
        return text
    return text.rstrip() + "\n\n" + " ".join(to_add)


def truncate(text: str, limit: int = 2200, ellipsis: str = "…") -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(ellipsis))].rstrip() + ellipsis


def strip_mentions(text: str) -> str:
    return re.sub(r"@\w+", "", text or "").strip()
