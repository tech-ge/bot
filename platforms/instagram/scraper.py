"""Optional scraping fallback (no API). Use sparingly — ToS risk."""
from __future__ import annotations

from typing import Any

from loguru import logger


class InstagramScraper:
    def __init__(self, username: str) -> None:
        self.username = username

    async def profile(self, handle: str) -> dict[str, Any]:
        logger.warning("Scraper fallback invoked for @{h}", h=handle)
        return {"handle": handle, "source": "scraper", "data": {}}
