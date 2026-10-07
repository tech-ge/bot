"""Create the database schema."""
from __future__ import annotations

import asyncio

from loguru import logger

from config.logging_setup import setup_logging
from data.db import init_db


async def main() -> None:
    setup_logging()
    await init_db()
    logger.success("DB seeded")


if __name__ == "__main__":
    asyncio.run(main())
