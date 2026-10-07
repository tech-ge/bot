"""Post a single message to one account (ad-hoc)."""
from __future__ import annotations

import argparse
import asyncio

from config.logging_setup import setup_logging
from core.bot import BotManager
from config.settings import settings


async def main(account_id: str, content: str) -> None:
    setup_logging()
    mgr = BotManager(settings=settings)
    await mgr.load_accounts()
    bot = next((a for a in mgr.accounts if a.id == account_id), None)
    if bot is None:
        raise SystemExit(f"Account {account_id} not found")
    await bot.start()
    try:
        result = await bot.perform("post", content=content, media=[])
        print(result)
    finally:
        await bot.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("account_id")
    parser.add_argument("content")
    args = parser.parse_args()
    asyncio.run(main(args.account_id, args.content))
