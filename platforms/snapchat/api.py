"""
Snapchat API wrapper — Snap Kit / Marketing API.
Note: organic account automation is heavily restricted; most actions here
target the Marketing API (ads, creatives, audiences).
"""
from __future__ import annotations

from typing import Any

import httpx

from config.settings import settings

SNAP_BASE = "https://adsapi.snapchat.com/v1"


class SnapchatAPI:
    def __init__(self) -> None:
        self.client_id = settings.env_settings.snap_client_id
        self.client_secret = settings.env_settings.snap_client_secret
        self.token = settings.env_settings.snap_access_token
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    async def list_campaigns(self, ad_account_id: str) -> dict[str, Any]:
        url = f"{SNAP_BASE}/adaccounts/{ad_account_id}/campaigns"
        r = await self._client.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    async def create_creative(self, ad_account_id: str, name: str,
                              media_url: str) -> dict[str, Any]:
        url = f"{SNAP_BASE}/adaccounts/{ad_account_id}/creatives"
        payload = {
            "name": name,
            "type": "SNAP_AD",
            "headline": name,
            "top_snap_media_id": media_url,
        }
        r = await self._client.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()
        return r.json()
