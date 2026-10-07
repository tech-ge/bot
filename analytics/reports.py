"""Simple report builders."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select

from data.db import session_scope
from data.models import Action, Post


async def actions_last_days(days: int = 7) -> dict[str, int]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    async with session_scope() as s:
        rows = (await s.execute(
            select(Action).where(Action.created_at >= since)
        )).scalars().all()
    counter = Counter(r.action for r in rows)
    return dict(counter)


async def posts_per_platform() -> dict[str, int]:
    async with session_scope() as s:
        rows = (await s.execute(select(Post))).scalars().all()
    counter = Counter(r.platform for r in rows)
    return dict(counter)


async def full_report() -> dict[str, Any]:
    return {
        "actions_7d": await actions_last_days(7),
        "posts_by_platform": await posts_per_platform(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
