"""Twitter/X API v2 wrapper via Tweepy."""
from __future__ import annotations

from typing import Any

import tweepy

from config.settings import settings


class TwitterAPI:
    def __init__(self) -> None:
        e = settings.env_settings
        self.client = tweepy.Client(
            bearer_token=e.tw_bearer_token or None,
            consumer_key=e.tw_api_key or None,
            consumer_secret=e.tw_api_secret or None,
            access_token=e.tw_access_token or None,
            access_token_secret=e.tw_access_secret or None,
            wait_on_rate_limit=True,
        )

    async def close(self) -> None:
        return None

    def post_tweet(self, text: str) -> dict[str, Any]:
        resp = self.client.create_tweet(text=text)
        return {"id": str(resp.data.get("id")), "text": text}

    def reply(self, tweet_id: str, text: str) -> dict[str, Any]:
        resp = self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
        return {"id": str(resp.data.get("id")), "text": text}

    def like(self, tweet_id: str) -> dict[str, Any]:
        resp = self.client.like(tweet_id)
        return {"ok": bool(resp.data.get("liked"))}

    def follow(self, user_id: str) -> dict[str, Any]:
        resp = self.client.follow_user(user_id)
        return {"ok": bool(resp.data.get("following"))}

    def dm(self, participant_id: str, text: str) -> dict[str, Any]:
        # Requires DM API access
        raise NotImplementedError("Twitter DM requires elevated access")
