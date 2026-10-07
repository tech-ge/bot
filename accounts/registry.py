"""Account registry — loads config/accounts.yaml and every per-account YAML."""
from __future__ import annotations

from pathlib import Path

import yaml
from loguru import logger

from accounts.account import Account
from config.settings import settings


class AccountRegistry:
    def __init__(self, registry_path: Path | None = None) -> None:
        self.registry_path = registry_path or (
            settings.base_dir / "config" / "accounts.yaml"
        )
        self._accounts: list[Account] = []

    # ---- loading ----
    def load(self) -> list[Account]:
        self._accounts = []
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Account registry not found: {self.registry_path}"
            )

        data = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        entries = data.get("accounts", []) or []

        for entry in entries:
            cfg_file = entry.get("config_file")
            try:
                if cfg_file:
                    acct = Account.from_yaml(cfg_file)
                    # registry entry overrides YAML for these fields
                    acct.enabled = bool(entry.get("enabled", acct.enabled))
                    if entry.get("username"):
                        acct.username = str(entry["username"])
                    if entry.get("type"):
                        acct.type = str(entry["type"])
                    # keep config_file for downstream
                    acct.raw["config_file"] = cfg_file
                else:
                    acct = Account.from_dict(entry)
                self._accounts.append(acct)
            except Exception as exc:
                logger.exception("Failed to load account {id}: {e}",
                                 id=entry.get("id", "?"), e=exc)

        logger.info("AccountRegistry loaded {n} accounts", n=len(self._accounts))
        return list(self._accounts)

    # ---- accessors ----
    def all(self) -> list[Account]:
        return list(self._accounts)

    def enabled(self) -> list[Account]:
        return [a for a in self._accounts if a.enabled]

    def by_platform(self, platform: str) -> list[Account]:
        return [a for a in self._accounts if a.platform == platform]

    def get(self, account_id: str) -> Account | None:
        return next((a for a in self._accounts if a.id == account_id), None)

    def __len__(self) -> int:
        return len(self._accounts)

    def __iter__(self):
        return iter(self._accounts)


# module-level singleton for convenience
registry = AccountRegistry()
