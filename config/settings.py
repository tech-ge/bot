"""
Central settings loader for techgeo.
Reads from .env (via pydantic-settings) and config.yaml.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_YAML = BASE_DIR / "config.yaml"


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite+aiosqlite:///data/storage/techgeo.db"
    redis_url: str = "redis://localhost:6379/0"

    ig_graph_token: str = ""
    ig_username: str = ""
    ig_password: str = ""

    fb_graph_token: str = ""
    fb_page_id: str = ""

    snap_client_id: str = ""
    snap_client_secret: str = ""
    snap_access_token: str = ""

    tw_api_key: str = ""
    tw_api_secret: str = ""
    tw_bearer_token: str = ""
    tw_access_token: str = ""
    tw_access_secret: str = ""

    tg_bot_token_01: str = ""
    tg_bot_token_02: str = ""

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    proxy_file: str = "anti_detection/proxies.yaml"
    fingerprint_dir: str = "anti_detection/fingerprint_profiles"
    cookie_dir: str = "anti_detection/cookies"
    humanize_min_delay: float = 2.0
    humanize_max_delay: float = 8.0

    copyright_strict: bool = True
    asset_registry: str = "copyright_guard/asset_registry.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class Settings:
    def __init__(self) -> None:
        self.env_settings = EnvSettings()
        self.yaml: dict[str, Any] = _load_yaml(CONFIG_YAML)
        self.env = self.env_settings.env
        self.log_level = self.env_settings.log_level
        self.database_url = self.env_settings.database_url
        self.redis_url = self.env_settings.redis_url
        self.base_dir = BASE_DIR

    def get(self, *keys: str, default: Any = None) -> Any:
        node: Any = self.yaml
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def rate_limits(self) -> dict[str, Any]:
        return self.get("rate_limits", default={}) or {}

    @property
    def circuit_breaker(self) -> dict[str, Any]:
        return self.get("circuit_breaker", default={}) or {}

    @property
    def anti_detection(self) -> dict[str, Any]:
        return self.get("anti_detection", default={}) or {}

    @property
    def copyright_guard(self) -> dict[str, Any]:
        return self.get("copyright_guard", default={}) or {}

    @property
    def ai(self) -> dict[str, Any]:
        return self.get("ai", default={}) or {}

    @property
    def app(self) -> dict[str, Any]:
        return self.get("app", default={}) or {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
