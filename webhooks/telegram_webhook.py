"""Telegram webhook handler (aiogram Dispatcher)."""
from __future__ import annotations

from typing import Any

from loguru import logger


async def handle(payload: dict[str, Any]) -> dict[str, Any]:
    logger.debug("TG webhook update: {p}", p=payload)
    return {"ok": True}
