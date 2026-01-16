from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .base import (
    EventRecord,
    FixtureRecord,
    LineupRecord,
    Provider,
    ProviderMetadata,
    ResultRecord,
)


class OpenFootballCSVProvider(Provider):
    """Reads fixtures and results from an open, no-key CSV snapshot.

    The CSV is expected to live under `backend/sample_data/` and mirrors
    the openfootball dataset structure (league, season, teams, kickoff, scores).
    """

    meta = ProviderMetadata(
        name="openfootball-csv",
        description="OpenFootball CSV snapshot (no key, offline safe)",
        requires_api_key=False,
        rate_limit_per_minute=0,
        supports_live=False,
    )

    def __init__(self, base_path: Optional[Path] = None) -> None:
        self.base_path = base_path or Path(__file__).resolve().parent.parent / "sample_data"
        self.fixtures_file = self.base_path / "openfootball-fixtures.csv"
        self.results_file = self.base_path / "openfootball-results.csv"

    def _read_csv(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [row for row in reader]

    def _parse_datetime(self, value: str) -> datetime:
        # All snapshots are stored as UTC ISO strings
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        for row in self._read_csv(self.fixtures_file):
            yield FixtureRecord(
                fixture_id=row["fixture_id"],
                league=row["league"],
                season=row["season"],
                home_team=row["home_team"],
                away_team=row["away_team"],
                kickoff=self._parse_datetime(row["kickoff"]),
                venue=row.get("venue") or None,
                timezone="UTC",
            )

    def get_results(self) -> Iterable[ResultRecord]:
        for row in self._read_csv(self.results_file):
            yield ResultRecord(
                fixture_id=row["fixture_id"],
                league=row["league"],
                season=row["season"],
                home_team=row["home_team"],
                away_team=row["away_team"],
                kickoff=self._parse_datetime(row["kickoff"]),
                venue=row.get("venue") or None,
                timezone="UTC",
                home_score=int(row["home_score"]),
                away_score=int(row["away_score"]),
                status=row.get("status") or "FT",
            )

    def get_live_events(self) -> Iterable[EventRecord]:
        # OpenFootball snapshots are static; no live feed available.
        return []

    def get_lineups(self) -> Iterable[LineupRecord]:
        return []
