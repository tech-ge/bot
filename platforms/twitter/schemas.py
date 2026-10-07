from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Tweet(BaseModel):
    id: str
    text: str = ""


class TwActionResult(BaseModel):
    ok: bool
    raw: dict[str, Any] = {}
