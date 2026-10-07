"""Facebook Graph API wrapper (Pages + Messenger)."""
from __future__ import annotations

from typing import Any

import httpx

from config.settings import settings

GRAPH_BASE = "https://graph.facebook.com/v20.0"


class FacebookAPI:
    def __init__(self, page_id: str | None = None) -> None:
        self.token = settings.env_settings.fb_graph_token
        self.page_id = page_id or settings.env_settings.fb_page_id
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def post_page(self, message: str, link: str | None = None,
                        image_url: str | None = None) -> dict[str, Any]:
        if not self.token or not self.page_id:
            raise RuntimeError("FB_GRAPH_TOKEN or FB_PAGE_ID missing")
        if image_url:
            url = f"{GRAPH_BASE}/{self.page_id}/photos"
            params = {"url": image_url, "caption": message,
                      "access_token": self.token}
        else:
            url = f"{GRAPH_BASE}/{self.page_id}/feed"
            params = {"message": message, "access_token": self.token}
            if link:
                params["link"] = link
        r = await self._client.post(url, params=params)
        r.raise_for_status()
        return r.json()

    async def reply_comment(self, comment_id: str, message: str) -> dict[str, Any]:
        url = f"{GRAPH_BASE}/{comment_id}/comments"
        r = await self._client.post(
            url, params={"message": message, "access_token": self.token}
        )
        r.raise_for_status()
        return r.json()

    async def send_message(self, recipient_id: str, text: str) -> dict[str, Any]:
        url = f"{GRAPH_BASE}/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "access_token": self.token,
        }
        r = await self._client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    async def like(self, object_id: str) -> dict[str, Any]:
        url = f"{GRAPH_BASE}/{object_id}/likes"
        r = await self._client.post(url, params={"access_token": self.token})
        r.raise_for_status()
        return r.json()
