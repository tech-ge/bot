"""Time helpers."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).isoformat()


def day_key(dt: datetime | None = None) -> str:
    return (dt or utcnow()).strftime("%Y-%m-%d")
