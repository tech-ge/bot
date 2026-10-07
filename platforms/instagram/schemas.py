"""Instagram request/response schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class IGPost(BaseModel):
    id: str
    caption: str = ""
    media_url: str | None = None
    permalink: str | None = None


class IGActionResult(BaseModel):
    ok: bool
    raw: dict[str, Any] = {}
