"""
Fetch and extract clean text from web pages.
Uses trafilatura (best for article extraction) with BS4 fallback.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import httpx
from loguru import logger

DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


@dataclass
class ScrapedPage:
    url: str
    title: str = ""
    text: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    ok: bool = True
    error: str = ""


class WebScraper:
    def __init__(self, *, timeout: float = 20.0, user_agent: str = DEFAULT_UA) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent,
                        "Accept-Language": "en-US,en;q=0.9"}

    async def fetch(self, url: str) -> ScrapedPage:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers,
                follow_redirects=True
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
        except Exception as exc:
            logger.warning("Fetch failed {u}: {e}", u=url, e=exc)
            return ScrapedPage(url=url, ok=False, error=str(exc))

        return await asyncio.to_thread(self._extract, url, html)

    def _extract(self, url: str, html: str) -> ScrapedPage:
        title = ""
        text = ""
        meta: dict[str, Any] = {}

        try:
            import trafilatura  # type: ignore
            text = trafilatura.extract(html, include_comments=False,
                                       include_tables=False) or ""
            meta_raw = trafilatura.extract_metadata(html)
            if meta_raw:
                title = getattr(meta_raw, "title", "") or ""
                meta["author"] = getattr(meta_raw, "author", "")
                meta["date"] = getattr(meta_raw, "date", "")
                meta["sitename"] = getattr(meta_raw, "sitename", "")
        except Exception as exc:
            logger.debug("trafilatura failed for {u}: {e}", u=url, e=exc)

        if not text:
            try:
                from bs4 import BeautifulSoup  # type: ignore
                soup = BeautifulSoup(html, "lxml")
                for tag in soup(["script", "style", "noscript", "header",
                                 "footer", "nav", "aside"]):
                    tag.decompose()
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                text = " ".join(soup.get_text(" ").split())
            except Exception as exc:
                logger.debug("BS4 fallback failed for {u}: {e}", u=url, e=exc)

        if not text:
            return ScrapedPage(url=url, ok=False, error="no_text_extracted")

        return ScrapedPage(url=url, title=title,
                           text=text[:20000], meta=meta, ok=True)

    async def fetch_many(self, urls: list[str],
                         concurrency: int = 4) -> list[ScrapedPage]:
        sem = asyncio.Semaphore(concurrency)

        async def _one(u: str) -> ScrapedPage:
            async with sem:
                return await self.fetch(u)

        return await asyncio.gather(*(_one(u) for u in urls))


web_scraper = WebScraper()
