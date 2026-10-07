"""In-memory + optional persistent state for dedupe / memory."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


class StateManager:
    def __init__(self, namespace: str) -> None:
        self.namespace = namespace
        self._path = settings.base_dir / "data" / "storage" / f"state_{namespace}.json"
        self._data: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def load(self) -> None:
        async with self._lock:
            if self._path.exists():
                try:
                    self._data = json.loads(self._path.read_text(encoding="utf-8"))
                    logger.debug("Loaded state for {ns}: {n} keys",
                                 ns=self.namespace, n=len(self._data))
                except Exception as exc:
                    logger.exception("Failed to load state {p}: {e}",
                                     p=self._path, e=exc)
                    self._data = {}
            else:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                self._data = {}

    async def save(self) -> None:
        async with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(self._data, indent=2, default=str),
                encoding="utf-8",
            )

    async def get(self, key: str, default: Any = None) -> Any:
        async with self._lock:
            return self._data.get(key, default)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._data[key] = value

    async def seen(self, key: str) -> bool:
        async with self._lock:
            return key in self._data

    async def mark_seen(self, key: str, value: Any = True) -> None:
        async with self._lock:
            self._data[key] = value

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()
