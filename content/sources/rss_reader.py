"""RSS/Atom feed reader using feedparser."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class FeedItem:
    title: str
    link: str
    summary: str = ""
    published: str = ""
    source: str = ""


class RSSReader:
    async def fetch(self, feed_url: str, limit: int = 10) -> list[FeedItem]:
        return await asyncio.to_thread(self._fetch_sync, feed_url, limit)

    def _fetch_sync(self, feed_url: str, limit: int) -> list[FeedItem]:
        try:
            import feedparser  # type: ignore
        except ImportError:
            logger.warning("feedparser not installed")
            return []

        try:
            parsed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.warning("RSS parse failed {u}: {e}", u=feed_url, e=exc)
            return []

        source = parsed.feed.get("title", "") if hasattr(parsed, "feed") else ""
        out: list[FeedItem] = []
        for entry in parsed.entries[:limit]:
            out.append(FeedItem(
                title=entry.get("title", ""),
                link=entry.get("link", ""),
                summary=entry.get("summary", ""),
                published=entry.get("published", ""),
                source=source,
            ))
        logger.debug("RSS {u}: {n} items", u=feed_url, n=len(out))
        return out

    async def fetch_many(self, feeds: list[str], limit: int = 10) -> list[FeedItem]:
        results = await asyncio.gather(
            *(self.fetch(f, limit) for f in feeds),
            return_exceptions=True,
        )
        items: list[FeedItem] = []
        for r in results:
            if isinstance(r, Exception):
                logger.warning("Feed failed: {e}", e=r)
                continue
            items.extend(r)
        return items


rss_reader = RSSReader()
