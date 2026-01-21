from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


TRUTHY_VALUES = {"1", "true", "yes", "on"}


class DataMode(str, Enum):
    FREE_ONLY = "free-only"
    HYBRID = "hybrid"
    PREMIUM_ENABLED = "premium-enabled"

    @classmethod
    def from_env(cls, value: str) -> "DataMode":
        normalized = (value or "").strip().lower().replace("_", "-")
        for mode in cls:
            if mode.value == normalized:
                return mode
        warnings.warn(f"Unknown GFPS_DATA_MODE '{value}', falling back to free-only")
        return cls.FREE_ONLY


@dataclass
class ProviderToggle:
    enabled: bool = True
    priority: int = 100
    refresh_seconds: Optional[int] = None


@dataclass
class DataSourceSettings:
    mode: DataMode = DataMode.FREE_ONLY
    provider_overrides: Dict[str, ProviderToggle] = field(default_factory=dict)
    api_keys: Dict[str, str] = field(default_factory=dict)
    live_network_enabled: bool = False


def _env_flag(name: str, default: str = "0") -> bool:
    return (os.getenv(name, default) or "").lower() in TRUTHY_VALUES


def load_settings_from_env() -> DataSourceSettings:
    mode = DataMode.from_env(os.getenv("GFPS_DATA_MODE", "free-only"))
    overrides: Dict[str, ProviderToggle] = {
        "openfootball-csv": ProviderToggle(enabled=True, priority=5, refresh_seconds=86400),
        "football-data.org": ProviderToggle(
            enabled=_env_flag("ENABLE_FOOTBALL_DATA", "1"),
            priority=15,
            refresh_seconds=6 * 3600,
        ),
        "web-scraper": ProviderToggle(
            enabled=_env_flag("ENABLE_WEB_SCRAPER", "1"),
            priority=20,
            refresh_seconds=3600,
        ),
        "openligadb-live": ProviderToggle(
            enabled=_env_flag("ENABLE_OPENLIGADB", "1"),
            priority=25,
            refresh_seconds=120,
        ),
        "api-football-premium": ProviderToggle(
            enabled=_env_flag("ENABLE_API_FOOTBALL", "0"),
            priority=70,
            refresh_seconds=60,
        ),
        "api-football-stub": ProviderToggle(
            enabled=_env_flag("ENABLE_API_FOOTBALL_STUB", "0"),
            priority=80,
            refresh_seconds=60,
        ),
    }
    api_keys = {
        "football-data.org": os.getenv("FOOTBALL_DATA_API_KEY", ""),
        "api-football-premium": os.getenv("APIFOOTBALL_KEY", ""),
    }
    live_network_enabled = _env_flag("ENABLE_LIVE_NETWORK", "0")
    return DataSourceSettings(
        mode=mode,
        provider_overrides=overrides,
        api_keys=api_keys,
        live_network_enabled=live_network_enabled,
    )
