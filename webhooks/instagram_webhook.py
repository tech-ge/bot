"""Instagram (Meta) webhook handler."""
from __future__ import annotations

from typing import Any

from loguru import logger


async def handle(payload: dict[str, Any]) -> dict[str, Any]:
    logger.debug("IG webhook: {p}", p=payload)
    return {"ok": True}
