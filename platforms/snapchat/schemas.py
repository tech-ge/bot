from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SnapAction(BaseModel):
    ok: bool
    raw: dict[str, Any] = {}
