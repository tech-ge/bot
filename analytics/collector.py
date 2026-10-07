"""Persist metrics and action logs into the database."""
from __future__ import annotations

from typing import Any

from loguru import logger
from sqlalchemy import select

from data.db import session_scope
from data.models import Account, Action, Metric, Post


async def ensure_account(account_id: str, platform: str, type_: str,
                         username: str, enabled: bool = True) -> None:
    async with session_scope() as s:
        existing = await s.execute(
            select(Account).where(Account.account_id == account_id)
        )
        if existing.scalar_one_or_none() is None:
            s.add(Account(account_id=account_id, platform=platform,
                          type=type_, username=username, enabled=enabled))


async def record_action(account_id: str, action: str, status: str,
                        payload: dict[str, Any] | None = None,
                        error: str | None = None) -> None:
    async with session_scope() as s:
        s.add(Action(account_id=account_id, action=action, status=status,
                     payload=payload or {}, error=error))


async def record_post(account_id: str, platform: str, content: str,
                      media: list[str] | None = None,
                      external_id: str | None = None) -> None:
    async with session_scope() as s:
        s.add(Post(account_id=account_id, platform=platform, content=content,
                   media=media or [], external_id=external_id))


async def record_metric(account_id: str, name: str, value: float) -> None:
    async with session_scope() as s:
        s.add(Metric(account_id=account_id, name=name, value=value))


async def summary() -> dict[str, int]:
    async with session_scope() as s:
        accounts = (await s.execute(select(Account))).scalars().all()
        actions = (await s.execute(select(Action))).scalars().all()
        posts = (await s.execute(select(Post))).scalars().all()
    logger.debug("Summary: {a} accounts, {ac} actions, {p} posts",
                 a=len(accounts), ac=len(actions), p=len(posts))
    return {"accounts": len(accounts), "actions": len(actions), "posts": len(posts)}
