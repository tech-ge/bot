from __future__ import annotations

from typing import Any

from platforms.facebook.api import FacebookAPI


class FacebookActions:
    def __init__(self, api: FacebookAPI) -> None:
        self.api = api

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        image_url = media[0] if media else None
        return await self.api.post_page(content, image_url=image_url)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        return await self.api.reply_comment(target_id, content)

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        return await self.api.send_message(user_id, content)

    async def like(self, target_id: str) -> dict[str, Any]:
        return await self.api.like(target_id)

    async def follow(self, user_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported_via_graph"}
