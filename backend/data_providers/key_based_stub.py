from __future__ import annotations

import os
from typing import Iterable

from .base import (
    EventRecord,
    FixtureRecord,
    LineupRecord,
    Provider,
    ProviderMetadata,
    ProviderTier,
    ResultRecord,
)


class KeyBasedStubProvider(Provider):
    """Optional, disabled-by-default provider that requires an API key.

    This keeps the ingestion layer pluggable while ensuring the system
    still runs without credentials. The stub returns no data when the
    key is missing.
    """

    meta = ProviderMetadata(
        name="api-football-stub",
        description="Placeholder for key-based providers (e.g., API-Football)",
        data_types={"fixtures", "results", "events", "odds"},
        requires_api_key=True,
        rate_limit_per_minute=30,
        supports_live=True,
        tier=ProviderTier.PREMIUM,
        reliability=0.85,
        auth_note="Set APIFOOTBALL_KEY to activate",
        priority=80,
    )

    def __init__(self, api_key_env: str = "API_FOOTBALL_KEY") -> None:
        self.api_key = os.getenv(api_key_env)

    def _guard(self) -> bool:
        return bool(self.api_key)

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        if not self._guard():
            return []
        return []

    def get_results(self) -> Iterable[ResultRecord]:
        if not self._guard():
            return []
        return []

    def get_live_events(self) -> Iterable[EventRecord]:
        if not self._guard():
            return []
        return []

    def get_lineups(self) -> Iterable[LineupRecord]:
        if not self._guard():
            return []
        return []
