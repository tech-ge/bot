from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FBPost(BaseModel):
    id: str
    message: str = ""
    permalink: str | None = None


class FBActionResult(BaseModel):
    ok: bool
    raw: dict[str, Any] = {}
