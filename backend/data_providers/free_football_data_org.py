from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import httpx

from .base import FixtureRecord, Provider, ProviderMetadata, ProviderTier, ResultRecord
from .utils import parse_utc_datetime


class FootballDataOrgProvider(Provider):
    """Free-tier friendly provider with offline fallback snapshots.

    The free tier is rate-limited; by default we operate in offline mode
    and only hit the network when explicitly enabled by the user.
    """

    meta = ProviderMetadata(
        name="football-data.org",
        description="Free community fixtures/results (rate-limited)",
        data_types={"fixtures", "results"},
        requires_api_key=True,
        rate_limit_per_minute=10,
        supports_live=False,
        tier=ProviderTier.FREE,
        reliability=0.55,
        refresh_seconds=6 * 3600,
        auth_note="Set FOOTBALL_DATA_API_KEY to enable live calls",
        priority=15,
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_path: Optional[Path] = None,
        allow_network: bool = False,
    ) -> None:
        self.api_key = api_key
        self.base_path = base_path or Path(__file__).resolve().parent.parent / "sample_data"
        self.fixtures_file = self.base_path / "football-data-fixtures.json"
        self.results_file = self.base_path / "football-data-results.json"
        self.allow_network = allow_network

    def _load_local(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _fetch(self, endpoint: str) -> list[dict]:
        if not self.allow_network or not self.api_key:
            return []
        headers = {"X-Auth-Token": self.api_key}
        url = f"https://api.football-data.org/v4/{endpoint}"
        try:
            resp = httpx.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("matches") or []
        except httpx.HTTPError:
            return []

    def _fixtures_payload(self) -> list[dict]:
        data = self._load_local(self.fixtures_file)
        if not data:
            data = self._fetch("matches?status=SCHEDULED")
        return data

    def _results_payload(self) -> list[dict]:
        data = self._load_local(self.results_file)
        if not data:
            data = self._fetch("matches?status=FINISHED")
        return data

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        # Local snapshot first to avoid network dependency.
        for row in self._fixtures_payload():
            yield FixtureRecord(
                fixture_id=str(row["id"]),
                league=row.get("competition") or "unknown",
                season=str(row.get("season") or "unknown"),
                home_team=row.get("homeTeam") or "TBD",
                away_team=row.get("awayTeam") or "TBD",
                kickoff=parse_utc_datetime(row.get("utcDate"), default_future=True),
                venue=row.get("venue"),
                timezone="UTC",
            )

    def get_results(self) -> Iterable[ResultRecord]:
        for row in self._results_payload():
            full_time = row.get("score", {}).get("fullTime", {})
            yield ResultRecord(
                fixture_id=str(row["id"]),
                league=row.get("competition") or "unknown",
                season=str(row.get("season") or "unknown"),
                home_team=row.get("homeTeam") or "TBD",
                away_team=row.get("awayTeam") or "TBD",
                kickoff=parse_utc_datetime(row.get("utcDate"), default_future=True),
                venue=row.get("venue"),
                timezone="UTC",
                home_score=int(full_time.get("home") or 0),
                away_score=int(full_time.get("away") or 0),
                status=row.get("status") or "FT",
            )
