"""
Instagram API wrapper.
Prefers Graph API (official) and falls back to instagrapi (unofficial).
"""
from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from config.settings import settings

GRAPH_BASE = "https://graph.facebook.com/v20.0"


class InstagramAPI:
    def __init__(self, username: str) -> None:
        self.username = username
        self.token = settings.env_settings.ig_graph_token
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def graph_post(self, ig_user_id: str, caption: str,
                         image_url: str | None = None) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("IG_GRAPH_TOKEN not set")
        if image_url:
            url = f"{GRAPH_BASE}/{ig_user_id}/media"
            params = {"image_url": image_url, "caption": caption,
                      "access_token": self.token}
            r = await self._client.post(url, params=params)
            r.raise_for_status()
            creation_id = r.json()["id"]
            publish_url = f"{GRAPH_BASE}/{ig_user_id}/media_publish"
            r2 = await self._client.post(
                publish_url,
                params={"creation_id": creation_id, "access_token": self.token},
            )
            r2.raise_for_status()
            return r2.json()
        raise RuntimeError("Instagram requires media_url for posting")

    # ---- unofficial fallback (instagrapi) ----
    def instagrapi_client(self) -> Any:
        try:
            from instagrapi import Client  # type: ignore
        except ImportError as exc:
            raise RuntimeError("instagrapi not installed") from exc

        cl = Client()
        user = settings.env_settings.ig_username
        pwd = settings.env_settings.ig_password
        if user and pwd:
            try:
                cl.login(user, pwd)
            except Exception as exc:
                logger.exception("instagrapi login failed for {u}: {e}",
                                 u=self.username, e=exc)
                raise
        return cl
