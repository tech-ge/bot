"""
Scheduled posting strategy with AI generation + web/RSS sourcing + images.
"""
from __future__ import annotations

import random
from typing import Any

from content.generator import content_generator
from content.images.pipeline import image_pipeline
from content.sources.aggregator import aggregator
from copyright_guard.input_checker import InputChecker
from copyright_guard.output_checker import OutputChecker
from strategies.base_strategy import BaseStrategy


class ContentPostingStrategy(BaseStrategy):
    name = "content_posting"

    def __init__(
        self,
        bot: Any,
        topics: list[str] | None = None,
        images: list[str] | None = None,
        *,
        feeds: list[str] | None = None,
        source_urls: list[str] | None = None,
        image_urls: list[str] | None = None,
        ai_image_prompt: str | None = None,
        max_len: int = 280,
        tone: str = "informative",
        watermark: str = "",
    ) -> None:
        super().__init__(bot)
        self.topics = topics or ["general update"]
        self.local_images = images or []
        self.feeds = feeds or []
        self.source_urls = source_urls or []
        self.image_urls = image_urls or []
        self.ai_image_prompt = ai_image_prompt
        self.max_len = max_len
        self.tone = tone
        self.watermark = watermark

        self.input_checker = InputChecker()
        self.output_checker = OutputChecker()

    # ---------- text ----------
    async def _text_from_source(self) -> str | None:
        if not self.feeds and not self.source_urls:
            return None
        items = await aggregator.gather(feeds=self.feeds, urls=self.source_urls)
        if not items:
            return None
        item = random.choice(items)
        text = await content_generator.generate_from_item(
            item, platform=self.bot.platform, tone=self.tone,
            max_len=self.max_len,
        )
        self.log.debug("Sourced from {src} ({u})", src=item.source, u=item.url)
        return text

    async def _text_from_topic(self) -> str:
        topic = random.choice(self.topics)
        return await content_generator.generate_post(
            topic, platform=self.bot.platform,
            tone=self.tone, max_len=self.max_len,
        )

    # ---------- images ----------
    async def _images_for_post(self) -> list[str]:
        has_any_source = bool(
            self.local_images or self.image_urls or self.ai_image_prompt
        )
        if not has_any_source:
            return []
        try:
            return await image_pipeline.prepare(
                self.bot.platform,
                local_paths=self.local_images,
                source_urls=self.image_urls,
                ai_prompt=self.ai_image_prompt,
                watermark=self.watermark,
                count=1,
            )
        except Exception as exc:
            self.log.warning("Image pipeline failed: {e}", e=exc)
            return []

    # ---------- main ----------
    async def run_once(self) -> None:
        text = await self._text_from_source() or await self._text_from_topic()

        out = self.output_checker.check(text)
        if not out.ok:
            self.log.warning("Post rejected by output checker: {r}",
                             r=out.reason)
            return

        media = await self._images_for_post()
        result = await self.bot.perform("post", content=text, media=media)
        self.log.info("Posted: {r} (media={m})", r=result, m=len(media))
        await self.cool_down()
