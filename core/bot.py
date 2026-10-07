"""
BotManager — loads accounts, wires platform adapters, runs them.
Also defines BaseBot (per-account runtime).
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from config.settings import Settings, settings as default_settings
from core.circuit_breaker import CircuitBreaker
from core.events import bus
from core.rate_limiter import rate_limiter
from core.scheduler import scheduler
from core.state_manager import StateManager
from core.task_queue import TaskQueue


# ────────────────────────────────────────────────────────────
# BaseBot — one instance per account
# ────────────────────────────────────────────────────────────
class BaseBot:
    def __init__(self, account_cfg: dict[str, Any], app_settings: Settings) -> None:
        self.cfg = account_cfg
        self.settings = app_settings
        self.id: str = account_cfg["id"]
        self.platform: str = account_cfg["platform"]
        self.type: str = account_cfg.get("type", "personal")
        self.username: str = account_cfg.get("username", "")
        self.enabled: bool = bool(account_cfg.get("enabled", True))

        # Merge per-account YAML (limits, topics, auth, isolation) into cfg.
        self._merge_account_yaml()

        self.state = StateManager(self.id)
        self.breaker = CircuitBreaker(**{
            "warning_threshold": self.settings.circuit_breaker.get(
                "warning_threshold", 1),
            "pause_minutes": self.settings.circuit_breaker.get("pause_minutes", 45),
            "max_trips_per_day": self.settings.circuit_breaker.get(
                "max_trips_per_day", 3),
        })
        self._adapter: Any = None
        self._running = False

    # ----- internals -----
    def _merge_account_yaml(self) -> None:
        cfg_file = self.cfg.get("config_file")
        if not cfg_file:
            return
        path = self.settings.base_dir / cfg_file
        if not path.exists():
            logger.warning("Account YAML missing for {id}: {p}",
                           id=self.id, p=path)
            return
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.exception("Bad account YAML {p}: {e}", p=path, e=exc)
            return
        # Shallow merge — per-account file wins on conflicts.
        self.cfg = {**data, **self.cfg}

    # ----- lifecycle -----
    async def start(self) -> None:
        if not self.enabled:
            logger.info("Account {id} disabled — skipping", id=self.id)
            return
        await self.state.load()
        self._configure_rate_limits()
        self._adapter = self._build_adapter()
        if self._adapter is None:
            logger.error("No adapter for platform {p} (account {id})",
                         p=self.platform, id=self.id)
            return
        try:
            await self._adapter.login()
        except Exception as exc:
            logger.exception("Login failed for {id}: {e}", id=self.id, e=exc)
            await self.breaker.record_warning(self.id, reason="login_failed")
            return
        self._running = True
        logger.success("Account {id} ({p}) started", id=self.id, p=self.platform)

    async def stop(self) -> None:
        self._running = False
        if self._adapter is not None:
            try:
                await self._adapter.close()
            except Exception:
                pass
        await self.state.save()
        logger.info("Account {id} stopped", id=self.id)

    def _configure_rate_limits(self) -> None:
        # Prefer per-account limits; fall back to platform; then default.
        limits = (
            self.cfg.get("limits")
            or self.settings.rate_limits.get(self.platform)
            or self.settings.rate_limits.get("default")
            or {}
        )
        per_min = float(
            limits.get("actions_per_minute")
            or limits.get("messages_per_minute")
            or 20
        )
        rate_limiter.configure(
            self.id, "action",
            capacity=max(1, int(per_min)),
            refill_per_sec=per_min / 60.0,
        )

    def _build_adapter(self) -> Any:
        try:
            if self.platform == "instagram":
                from platforms.instagram.adapter import InstagramAdapter
                return InstagramAdapter(self)
            if self.platform == "facebook":
                from platforms.facebook.adapter import FacebookAdapter
                return FacebookAdapter(self)
            if self.platform == "snapchat":
                from platforms.snapchat.adapter import SnapchatAdapter
                return SnapchatAdapter(self)
            if self.platform == "twitter":
                from platforms.twitter.adapter import TwitterAdapter
                return TwitterAdapter(self)
            if self.platform == "telegram":
                from platforms.telegram.adapter import TelegramAdapter
                return TelegramAdapter(self)
        except ImportError as exc:
            logger.error("Adapter import failed for {p}: {e}",
                         p=self.platform, e=exc)
            return None
        return None

    # ----- public API used by strategies -----
    async def perform(self, action: str, **kwargs: Any) -> Any:
        await self.breaker.wait_if_paused(self.id)
        await rate_limiter.acquire(self.id, "action")
        try:
            method = getattr(self._adapter, action, None)
            if method is None:
                raise AttributeError(f"Adapter has no action '{action}'")
            result = await method(**kwargs)
            await bus.publish("action.success",
                              account_id=self.id, action=action)
            return result
        except Exception as exc:
            logger.exception("Action '{a}' failed on {id}: {e}",
                             a=action, id=self.id, e=exc)
            await bus.publish("action.failure",
                              account_id=self.id, action=action, error=str(exc))
            raise


# ────────────────────────────────────────────────────────────
# BotManager — top-level controller
# ────────────────────────────────────────────────────────────
class BotManager:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or default_settings
        self.accounts: list[BaseBot] = []
        self.queue = TaskQueue(
            max_concurrency=int(self.settings.app.get("max_concurrent_accounts", 10))
        )

    async def load_accounts(self) -> None:
        path = self.settings.base_dir / "config" / "accounts.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Missing account registry: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries = data.get("accounts", []) or []
        for entry in entries:
            self.accounts.append(BaseBot(entry, self.settings))
        logger.info("Loaded {n} accounts", n=len(self.accounts))

    async def start(self) -> None:
        scheduler.start()
        await self.queue.start(workers=4)
        for acc in self.accounts:
            await self.queue.submit(acc.start)
        logger.success("BotManager started with {n} accounts",
                       n=len(self.accounts))

    async def stop(self) -> None:
        for acc in self.accounts:
            await self.queue.submit(acc.stop)
        await self.queue.stop(drain=True)
        scheduler.shutdown(wait=False)
        logger.info("BotManager stopped")
