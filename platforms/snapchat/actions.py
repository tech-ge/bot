from __future__ import annotations

from typing import Any

from platforms.snapchat.api import SnapchatAPI


class SnapchatActions:
    def __init__(self, api: SnapchatAPI) -> None:
        self.api = api

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        return {"ok": False, "reason": "organic_posting_not_supported"}

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported"}

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported"}

    async def like(self, target_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported"}

    async def follow(self, user_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported"}
