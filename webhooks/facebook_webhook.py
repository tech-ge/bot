"""Facebook Messenger / Page webhook handler (framework-agnostic)."""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

from loguru import logger

from config.settings import settings


def verify_signature(body: bytes, signature: str) -> bool:
    secret = settings.env_settings.fb_graph_token.encode()
    if not secret or not signature:
        return False
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def handle(payload: dict[str, Any]) -> dict[str, Any]:
    logger.debug("FB webhook: {p}", p=payload)
    return {"ok": True}
