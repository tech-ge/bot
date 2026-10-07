"""Unified LLM client — supports OpenAI + Anthropic with fallback to echo."""
from __future__ import annotations

from typing import Any

from loguru import logger

from config.settings import settings


class LLMClient:
    def __init__(self) -> None:
        cfg = settings.ai
        self.provider: str = str(cfg.get("provider", "openai")).lower()
        self.model: str = str(cfg.get("model", "gpt-4o-mini"))
        self.temperature: float = float(cfg.get("temperature", 0.9))
        self.max_tokens: int = int(cfg.get("max_tokens", 500))
        self._openai: Any = None
        self._anthropic: Any = None
        self._init()

    def _init(self) -> None:
        env = settings.env_settings
        if self.provider == "openai" and env.openai_api_key:
            try:
                from openai import AsyncOpenAI  # type: ignore
                self._openai = AsyncOpenAI(api_key=env.openai_api_key)
                logger.info("LLM: OpenAI {m}", m=self.model)
                return
            except ImportError:
                logger.warning("openai SDK not installed")
        if self.provider == "anthropic" and env.anthropic_api_key:
            try:
                from anthropic import AsyncAnthropic  # type: ignore
                self._anthropic = AsyncAnthropic(api_key=env.anthropic_api_key)
                logger.info("LLM: Anthropic {m}", m=self.model)
                return
            except ImportError:
                logger.warning("anthropic SDK not installed")
        logger.warning("No LLM credentials — using echo fallback")

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        if self._openai is not None:
            return await self._openai_complete(prompt, system)
        if self._anthropic is not None:
            return await self._anthropic_complete(prompt, system)
        return self._echo(prompt)

    async def _openai_complete(self, prompt: str, system: str | None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            resp = await self._openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("OpenAI call failed: {e}", e=exc)
            return self._echo(prompt)

    async def _anthropic_complete(self, prompt: str, system: str | None) -> str:
        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system
            resp = await self._anthropic.messages.create(**kwargs)
            parts = []
            for block in resp.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts)
        except Exception as exc:
            logger.exception("Anthropic call failed: {e}", e=exc)
            return self._echo(prompt)

    @staticmethod
    def _echo(prompt: str) -> str:
        return f"[echo] {prompt[:180]}"


llm = LLMClient()
