"""Validation helpers."""
from __future__ import annotations

import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_HANDLE = re.compile(r"^@?[A-Za-z0-9_.]{3,30}$")


def is_email(s: str) -> bool:
    return bool(_EMAIL.match(s or ""))


def is_handle(s: str) -> bool:
    return bool(_HANDLE.match(s or ""))


def non_empty(s: str | None) -> bool:
    return bool((s or "").strip())
