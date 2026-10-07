"""Periodic cleanup: temp media, stale state files."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


def _older_than(path: Path, seconds: int) -> bool:
    try:
        return (time.time() - path.stat().st_mtime) > seconds
    except OSError:
        return False


def cleanup_temp_media(max_age_seconds: int = 86400) -> dict[str, Any]:
    root = settings.base_dir / "content" / "media" / "temp"
    removed = 0
    if root.exists():
        for p in root.rglob("*"):
            if p.is_file() and _older_than(p, max_age_seconds):
                try:
                    p.unlink()
                    removed += 1
                except OSError:
                    pass
    logger.info("Cleanup removed {n} temp files", n=removed)
    return {"removed": removed}
