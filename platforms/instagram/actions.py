"""Instagram high-level actions (built on api.py)."""
from __future__ import annotations

from typing import Any

from loguru import logger

from platforms.instagram.api import InstagramAPI


class InstagramActions:
    def __init__(self, api: InstagramAPI, ig_user_id: str) -> None:
        self.api = api
        self.ig_user_id = ig_user_id

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        image_url = media[0] if media else None
        if not image_url:
            logger.warning("Instagram post skipped: no media_url")
            return {"ok": False, "reason": "media_required"}
        return await self.api.graph_post(self.ig_user_id, content, image_url)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        # Graph comment reply
        url = f"https://graph.facebook.com/v20.0/{target_id}/replies"
        r = await self.api._client.post(
            url, params={"message": content, "access_token": self.api.token}
        )
        r.raise_for_status()
        return r.json()

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        # IG Messaging API (requires messenger platform approval)
        url = f"https://graph.facebook.com/v20.0/{self.ig_user_id}/messages"
        payload = {
            "recipient": {"id": user_id},
            "message": {"text": content},
            "access_token": self.api.token,
        }
        r = await self.api._client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    async def like(self, target_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported_via_graph"}

    async def follow(self, user_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "not_supported_via_graph"}
