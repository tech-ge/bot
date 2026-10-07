"""Backfill analytics from logs (placeholder)."""
from __future__ import annotations

import asyncio

from loguru import logger

from config.logging_setup import setup_logging


async def main() -> None:
    setup_logging()
    logger.info("Backfill not implemented — placeholder")


if __name__ == "__main__":
    asyncio.run(main())
