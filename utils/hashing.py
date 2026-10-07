"""Hashing helpers."""
from __future__ import annotations

import hashlib


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def short_id(data: str | bytes, length: int = 12) -> str:
    return sha256_hex(data)[:length]
