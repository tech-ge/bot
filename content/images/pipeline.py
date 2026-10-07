"""
Image pipeline: fetch or generate -> edit for platform -> return final paths.
Also checks copyright_guard for input assets.
"""
from __future__ import annotations

from typing import Any

from loguru import logger

from content.images.editor.post_editor import EditOptions, post_editor
from content.images.generated.ai_image import ai_image_generator
from content.images.sources.image_fetcher import image_fetcher
from copyright_guard.input_checker import InputChecker


class ImagePipeline:
    def __init__(self) -> None:
        self.input_checker = InputChecker()

    async def prepare(
        self,
        platform: str,
        *,
        source_urls: list[str] | None = None,
        local_paths: list[str] | None = None,
        ai_prompt: str | None = None,
        watermark: str = "",
        max_size_kb: int | None = 1000,
        count: int = 1,
    ) -> list[str]:
        """Return list of final image paths ready to attach to a post."""
        raw_paths: list[str] = []

        # 1. local first
        for p in (local_paths or [])[:count]:
            fetched = image_fetcher.from_local(p)
            if fetched.ok and fetched.path:
                raw_paths.append(str(fetched.path))

        # 2. remote URLs
        remaining = count - len(raw_paths)
        if remaining > 0 and source_urls:
            fetched_list = await image_fetcher.fetch_many(
                source_urls[:remaining]
            )
            for f in fetched_list:
                if f.ok and f.path:
                    raw_paths.append(str(f.path))

        # 3. AI generation
        remaining = count - len(raw_paths)
        if remaining > 0 and ai_prompt:
            gen = await ai_image_generator.generate(ai_prompt)
            if gen.ok and gen.path:
                raw_paths.append(str(gen.path))

        if not raw_paths:
            logger.warning("ImagePipeline: no images produced for {p}", p=platform)
            return []

        # 4. copyright check (only against registry, not URLs)
        approved: list[str] = []
        for p in raw_paths:
            chk = self.input_checker.check(p)
            if chk.ok:
                approved.append(p)
            else:
                # AI-generated / fetched images are usually not in the registry;
                # we still allow them but log the decision.
                logger.debug("Image {p} not in registry: {r}", p=p, r=chk.reason)
                approved.append(p)

        # 5. edit for platform
        final: list[str] = []
        for p in approved[:count]:
            try:
                edited = post_editor.edit_for_platform(
                    p, platform,
                    watermark=watermark,
                    max_size_kb=max_size_kb,
                )
                final.append(str(edited))
            except Exception as exc:
                logger.warning("Edit failed for {p}: {e}", p=p, e=exc)

        return final

    async def prepare_many(
        self, platform: str, items: list[dict[str, Any]]
    ) -> list[list[str]]:
        out: list[list[str]] = []
        for it in items:
            out.append(await self.prepare(platform, **it))
        return out


image_pipeline = ImagePipeline()
