from __future__ import annotations

import os
from typing import Iterable, Optional

from .base import EventRecord, FixtureRecord, LineupRecord, Provider, ProviderMetadata, ProviderTier, ResultRecord


class ApiFootballProvider(Provider):
    """Premium-ready provider stubbed for optional activation."""

    meta = ProviderMetadata(
        name="api-football-premium",
        description="API-Football fixtures/results/live (premium, optional)",
        data_types={"fixtures", "results", "events", "odds"},
        requires_api_key=True,
        rate_limit_per_minute=60,
        supports_live=True,
        supports_odds=True,
        tier=ProviderTier.PREMIUM,
        reliability=0.9,
        refresh_seconds=60,
        auth_note="Set APIFOOTBALL_KEY to enable premium ingestion",
        priority=70,
    )

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("APIFOOTBALL_KEY")

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
