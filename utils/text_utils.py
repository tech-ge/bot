"""Text helpers."""
from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    return _WS.sub(" ", t).strip()


def slugify(text: str) -> str:
    t = normalize(text).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def chunks(text: str, size: int = 280) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]
