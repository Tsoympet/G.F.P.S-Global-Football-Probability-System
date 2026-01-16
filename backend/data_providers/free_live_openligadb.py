from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

import httpx

from .base import EventRecord, FixtureRecord, LineupRecord, Provider, ProviderMetadata, ProviderTier
from .utils import parse_utc_datetime


class OpenLigaDBLiveProvider(Provider):
    """Polling-based live provider with a bundled fallback snapshot."""

    meta = ProviderMetadata(
        name="openligadb-live",
        description="OpenLigaDB live scores (no auth, limited leagues)",
        data_types={"fixtures", "live_events"},
        requires_api_key=False,
        rate_limit_per_minute=30,
        supports_live=True,
        tier=ProviderTier.FREE,
        reliability=0.35,
        refresh_seconds=90,
        priority=25,
    )

    def __init__(
        self,
        base_path: Optional[Path] = None,
        allow_network: bool = False,
        season: str = "2024",
    ) -> None:
        self.base_path = base_path or Path(__file__).resolve().parent.parent / "sample_data"
        self.live_file = self.base_path / "openligadb-live.json"
        self.allow_network = allow_network
        self.season = season

    def _load_local(self) -> list[dict]:
        if not self.live_file.exists():
            return []
        with self.live_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _fetch_remote(self) -> list[dict]:
        if not self.allow_network:
            return []
        url = f"https://api.openligadb.de/getmatchdata/bl1/{self.season}"
        try:
            resp = httpx.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError:
            return []

    def _payload(self) -> list[dict]:
        data = self._load_local()
        if not data:
            data = self._fetch_remote()
        return data

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        for row in self._payload():
            kickoff = row.get("kickoff") or row.get("matchDateTimeUTC")
            kickoff_dt = parse_utc_datetime(kickoff)
            yield FixtureRecord(
                fixture_id=str(row.get("fixture_id") or row.get("matchID")),
                league=row.get("league") or "openligadb",
                season=str(row.get("season") or "2024"),
                home_team=row.get("home_team") or row.get("team1", {}).get("teamName") or "TBD",
                away_team=row.get("away_team") or row.get("team2", {}).get("teamName") or "TBD",
                kickoff=kickoff_dt,
                venue=row.get("venue"),
                timezone="UTC",
            )

    def get_live_events(self) -> Iterable[EventRecord]:
        for row in self._payload():
            for ev in row.get("events", []):
                yield EventRecord(
                    fixture_id=str(row.get("fixture_id") or row.get("matchID")),
                    minute=int(ev.get("minute") or 0),
                    team=ev.get("team") or "unknown",
                    type=ev.get("type") or "event",
                    player=ev.get("player") or None,
                )

    def get_lineups(self) -> Iterable[LineupRecord]:
        for row in self._payload():
            for lineup in row.get("lineups", []):
                yield LineupRecord(
                    fixture_id=str(row.get("fixture_id") or row.get("matchID")),
                    team=lineup.get("team") or "unknown",
                    players=lineup.get("players") or [],
                )
