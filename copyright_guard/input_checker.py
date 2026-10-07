"""Validate source assets before they enter the pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from config.settings import settings
from copyright_guard.license_db import get as get_license


@dataclass
class InputCheckResult:
    ok: bool
    reason: str = ""
    license_code: str = ""


class InputChecker:
    def __init__(self, registry_path: Path | None = None) -> None:
        self.registry_path = registry_path or (
            settings.base_dir / settings.env_settings.asset_registry
        )
        self.allowed = set(
            (settings.copyright_guard.get("allowed_licenses") or [])
        )
        self.strict = bool(
            settings.copyright_guard.get("strict", settings.env_settings.copyright_strict)
        )
        self._registry: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.registry_path.exists():
            logger.warning("No asset registry at {p}", p=self.registry_path)
            return
        try:
            data = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.exception("Failed to parse registry: {e}", e=exc)
            return
        for item in data.get("assets", []):
            self._registry[item["path"]] = item

    def check(self, asset_path: str | Path) -> InputCheckResult:
        key = str(asset_path)
        entry = self._registry.get(key)
        if entry is None:
            if self.strict:
                return InputCheckResult(False, "asset_not_registered")
            return InputCheckResult(True, "unregistered_allowed")

        code = str(entry.get("license", "")).upper()
        lic = get_license(code)
        if lic is None:
            return InputCheckResult(False, f"unknown_license:{code}", code)
        if self.allowed and code not in self.allowed:
            return InputCheckResult(False, f"license_not_allowed:{code}", code)
        if not lic.commercial_ok:
            return InputCheckResult(False, f"non_commercial:{code}", code)
        if not lic.modification_ok:
            return InputCheckResult(False, f"no_derivatives:{code}", code)
        return InputCheckResult(True, "", code)
