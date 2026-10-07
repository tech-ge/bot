"""
Fetch images from URLs or local paths.
Respects copyright_guard input_checker if used by caller.
"""
from __future__ import annotations

import asyncio
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

from content.media_utils import images_dir

DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@dataclass
class FetchedImage:
    url: str
    path: Path | None
    ok: bool
    error: str = ""
    bytes: int = 0


class ImageFetcher:
    def __init__(self, *, timeout: float = 20.0) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": DEFAULT_UA,
                        "Accept": "image/*,*/*;q=0.8"}

    def _guess_ext(self, url: str, content_type: str | None) -> str:
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext in ALLOWED_EXT:
            return ext
        if content_type:
            guess = mimetypes.guess_extension(content_type.split(";")[0].strip())
            if guess and guess.lower() in ALLOWED_EXT:
                return guess
        return ".jpg"

    async def fetch(self, url: str, *, prefix: str = "src") -> FetchedImage:
        try:
            async with httpx.AsyncClient(timeout=self.timeout,
                                         headers=self.headers,
                                         follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.content
                ctype = resp.headers.get("content-type")
        except Exception as exc:
            logger.warning("Image fetch failed {u}: {e}", u=url, e=exc)
            return FetchedImage(url=url, path=None, ok=False, error=str(exc))

        ext = self._guess_ext(url, ctype)
        out = images_dir() / f"{prefix}_{abs(hash(url)) & 0xffffffff:x}{ext}"
        out.write_bytes(data)
        logger.debug("Fetched image {u} -> {p} ({n} bytes)",
                     u=url, p=out, n=len(data))
        return FetchedImage(url=url, path=out, ok=True, bytes=len(data))

    async def fetch_many(self, urls: list[str],
                         concurrency: int = 4) -> list[FetchedImage]:
        sem = asyncio.Semaphore(concurrency)

        async def _one(u: str) -> FetchedImage:
            async with sem:
                return await self.fetch(u)

        return await asyncio.gather(*(_one(u) for u in urls))

    def from_local(self, path: str | Path) -> FetchedImage:
        p = Path(path)
        if not p.exists():
            return FetchedImage(url=str(p), path=None, ok=False,
                                error="not_found")
        return FetchedImage(url=str(p), path=p, ok=True,
                            bytes=p.stat().st_size)


image_fetcher = ImageFetcher()
