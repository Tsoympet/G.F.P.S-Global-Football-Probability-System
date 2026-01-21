"""
API-Football Premium Provider

⚠️ WARNING: This is an EXPENSIVE premium data provider ($50-300/month subscription)
⚠️ GFPS works perfectly fine WITHOUT this provider using FREE alternatives
⚠️ This provider is DISABLED BY DEFAULT and only activates when APIFOOTBALL_KEY is set

FREE alternatives (RECOMMENDED):
- OpenFootball CSV: Bundled fixtures/results (no key needed)
- Football-Data.org: Free API with rate limits (free API key)
- OpenLigaDB: Free live scores for German leagues (no key needed)

Only use this provider if you already have an API-Football subscription.
See docs/FREE_OPERATION_GUIDE.md for cost-free operation.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional

from .base import EventRecord, FixtureRecord, LineupRecord, Provider, ProviderMetadata, ProviderTier, ResultRecord


class ApiFootballProvider(Provider):
    """
    Premium provider for API-Football (EXPENSIVE - NOT RECOMMENDED).
    
    This provider is disabled by default and only activates when you provide an API key.
    GFPS works perfectly fine with free data providers instead.
    """

    meta = ProviderMetadata(
        name="api-football-premium",
        description="⚠️ EXPENSIVE API-Football ($50-300/mo) - Use FREE providers instead",
        data_types={"fixtures", "results", "events", "odds"},
        requires_api_key=True,
        rate_limit_per_minute=60,
        supports_live=True,
        supports_odds=True,
        tier=ProviderTier.PREMIUM,
        reliability=0.9,
        refresh_seconds=60,
        auth_note="⚠️ EXPENSIVE subscription required - FREE alternatives available",
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
