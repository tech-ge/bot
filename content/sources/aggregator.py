"""
Aggregate content from RSS + web sources, dedupe, and clean for posting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from content.sources.rss_reader import FeedItem, rss_reader
from content.sources.web_scraper import ScrapedPage, web_scraper
from utils.hashing import short_id
from utils.text_utils import normalize


@dataclass
class SourcedItem:
    id: str
    title: str
    text: str
    url: str = ""
    source: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


class ContentAggregator:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def _dedupe_key(self, text: str) -> str:
        return short_id(normalize(text).lower()[:400], length=16)

    def _from_feed(self, item: FeedItem) -> SourcedItem | None:
        text = normalize(item.summary or item.title)
        if not text:
            return None
        key = self._dedupe_key(text)
        if key in self._seen:
            return None
        self._seen.add(key)
        return SourcedItem(
            id=key, title=item.title, text=text,
            url=item.link, source=item.source or "rss",
        )

    def _from_page(self, page: ScrapedPage) -> SourcedItem | None:
        text = normalize(page.text[:2000])
        if not text:
            return None
        key = self._dedupe_key(text)
        if key in self._seen:
            return None
        self._seen.add(key)
        return SourcedItem(
            id=key, title=page.title, text=text,
            url=page.url, source=page.meta.get("sitename", "web"),
            meta=page.meta,
        )

    async def from_feeds(self, feeds: list[str], per_feed: int = 8) -> list[SourcedItem]:
        items = await rss_reader.fetch_many(feeds, limit=per_feed)
        out = [self._from_feed(i) for i in items]
        return [x for x in out if x is not None]

    async def from_urls(self, urls: list[str]) -> list[SourcedItem]:
        pages = await web_scraper.fetch_many(urls)
        out = [self._from_page(p) for p in pages if p.ok]
        return [x for x in out if x is not None]

    async def gather(self, *, feeds: list[str] | None = None,
                     urls: list[str] | None = None) -> list[SourcedItem]:
        results: list[SourcedItem] = []
        if feeds:
            results.extend(await self.from_feeds(feeds))
        if urls:
            results.extend(await self.from_urls(urls))
        logger.info("Aggregator gathered {n} unique items", n=len(results))
        return results

    def reset(self) -> None:
        self._seen.clear()


aggregator = ContentAggregator()
