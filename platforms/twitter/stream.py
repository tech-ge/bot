"""Filtered stream listener for Twitter/X."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

import tweepy
from loguru import logger

from config.settings import settings


class TwitterStream:
    def __init__(self, rules: list[str] | None = None) -> None:
        self.rules = rules or []
        self.bearer = settings.env_settings.tw_bearer_token

    def start(self, on_tweet: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        if not self.bearer:
            logger.warning("No TW_BEARER_TOKEN — stream disabled")
            return

        class _Client(tweepy.StreamingClient):
            def on_tweet(self, tweet):  # type: ignore[override]
                import asyncio
                asyncio.create_task(on_tweet({
                    "id": tweet.id,
                    "text": tweet.text,
                }))

        client = _Client(self.bearer)
        existing = client.get_rules()
        if existing.data:
            client.delete_rules([r.id for r in existing.data])
        for rule in self.rules:
            client.add_rules(tweepy.StreamRule(rule))
        client.filter()
