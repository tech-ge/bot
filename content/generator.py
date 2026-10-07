"""
Content generation — combines AI (LLM rewrite/summarize) with scraped sources.

Priority order:
  1. If a source URL or aggregated item is provided, rewrite it with the LLM.
  2. If only a topic is provided, generate fresh with the LLM.
  3. If no LLM credentials, fall back to extractive summarizer on scraped text.
"""
from __future__ import annotations

from typing import Any

from loguru import logger

from ai.llm_client import llm
from ai.summarizer import summarize
from content.sources.aggregator import SourcedItem, aggregator
from content.sources.web_scraper import web_scraper
from copyright_guard.output_checker import OutputChecker


class ContentGenerator:
    def __init__(self) -> None:
        self.output_checker = OutputChecker()

    # ---------- core AI calls ----------
    async def generate_post(
        self,
        topic: str,
        *,
        platform: str = "generic",
        tone: str = "informative",
        max_len: int = 280,
        source_url: str | None = None,
    ) -> str:
        source_text = ""
        if source_url:
            page = await web_scraper.fetch(source_url)
            if page.ok:
                source_text = page.text[:4000]
                logger.debug("Scraped {u} ({n} chars)",
                             u=source_url, n=len(source_text))

        if source_text:
            prompt = (
                f"Rewrite the following article as a {tone} {platform} post. "
                f"Keep it under {max_len} characters. No hashtags. No emojis. "
                f"Plain text only.\n\nArticle:\n{source_text}"
            )
        else:
            prompt = (
                f"Write a {tone} social media post for {platform} about: {topic}. "
                f"Keep it under {max_len} characters. No hashtags. No emojis. "
                "Plain text only."
            )

        text = await llm.complete(prompt)
        text = text.strip()
        if text.startswith("[echo]"):
            # LLM unavailable — summarize scraped text or the topic itself
            fallback = summarize(source_text) if source_text else topic
            text = fallback[:max_len]
        return text

    async def generate_from_item(
        self,
        item: SourcedItem,
        *,
        platform: str = "generic",
        tone: str = "informative",
        max_len: int = 280,
    ) -> str:
        return await self.generate_post(
            topic=item.title or item.text[:120],
            platform=platform, tone=tone, max_len=max_len,
            source_url=item.url or None,
        )

    async def generate_reply(self, incoming: str, tone: str = "friendly") -> str:
        prompt = (
            f"Reply in a {tone} tone to this message. One short sentence only:\n"
            f"{incoming}"
        )
        text = await llm.complete(prompt)
        return text.strip()

    async def generate_dm(self, context: str, tone: str = "professional") -> str:
        prompt = (
            f"Write a short {tone} DM based on this context. Under 240 characters:\n"
            f"{context}"
        )
        text = await llm.complete(prompt)
        return text.strip()

    async def generate_image_prompt(self, topic: str) -> str:
        prompt = f"Describe a simple, safe image for this topic in one sentence: {topic}"
        return (await llm.complete(prompt)).strip()

    # ---------- sourcing convenience ----------
    async def gather_and_generate(
        self,
        *,
        feeds: list[str] | None = None,
        urls: list[str] | None = None,
        platform: str = "generic",
        tone: str = "informative",
        max_len: int = 280,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        items = await aggregator.gather(feeds=feeds, urls=urls)
        out: list[dict[str, Any]] = []
        for item in items[:limit]:
            text = await self.generate_from_item(
                item, platform=platform, tone=tone, max_len=max_len
            )
            chk = self.output_checker.check(text)
            if not chk.ok:
                logger.warning("Generated post rejected: {r}", r=chk.reason)
                continue
            out.append({
                "source": item.source,
                "url": item.url,
                "title": item.title,
                "text": text,
            })
        return out


content_generator = ContentGenerator()
