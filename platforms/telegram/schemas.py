from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class TgMessage(BaseModel):
    chat_id: str
    text: str


class TgActionResult(BaseModel):
    ok: bool
    raw: dict[str, Any] = {}
