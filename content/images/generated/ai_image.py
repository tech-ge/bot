"""
AI image generation via OpenAI Images API (DALL·E / gpt-image-1).
Falls back gracefully if no key or SDK.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import httpx
from loguru import logger

from config.settings import settings
from content.media_utils import images_dir


@dataclass
class GeneratedImage:
    path: Path | None
    ok: bool
    error: str = ""
    prompt: str = ""


class AIImageGenerator:
    def __init__(self, *, model: str = "gpt-image-1", size: str = "1024x1024") -> None:
        self.model = model
        self.size = size
        self.api_key = settings.env_settings.openai_api_key
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def generate(self, prompt: str, *, prefix: str = "ai") -> GeneratedImage:
        if not self.api_key:
            logger.warning("No OPENAI_API_KEY — skipping AI image generation")
            return GeneratedImage(path=None, ok=False,
                                  error="no_api_key", prompt=prompt)

        url = "https://api.openai.com/v1/images/generations"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "prompt": prompt,
                   "size": self.size, "n": 1}
        try:
            r = await self._client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            item = data["data"][0]
            b64 = item.get("b64_json")
            img_url = item.get("url")
            out = images_dir() / f"{prefix}_{abs(hash(prompt)) & 0xffffffff:x}.png"
            if b64:
                out.write_bytes(base64.b64decode(b64))
            elif img_url:
                img = await self._client.get(img_url)
                img.raise_for_status()
                out.write_bytes(img.content)
            else:
                return GeneratedImage(path=None, ok=False,
                                      error="no_image_in_response", prompt=prompt)
            logger.info("AI image saved {p}", p=out)
            return GeneratedImage(path=out, ok=True, prompt=prompt)
        except Exception as exc:
            logger.exception("AI image generation failed: {e}", e=exc)
            return GeneratedImage(path=None, ok=False,
                                  error=str(exc), prompt=prompt)


ai_image_generator = AIImageGenerator()
