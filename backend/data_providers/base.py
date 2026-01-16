from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Protocol

from pydantic import BaseModel, field_validator


@dataclass
class ProviderMetadata:
    name: str
    description: str
    requires_api_key: bool = False
    rate_limit_per_minute: int = 60
    supports_live: bool = False


class FixtureRecord(BaseModel):
    fixture_id: str
    league: str
    season: str
    home_team: str
    away_team: str
    kickoff: datetime
    venue: Optional[str] = None
    timezone: Optional[str] = None

    @field_validator("fixture_id", "league", "season", "home_team", "away_team")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()


class ResultRecord(FixtureRecord):
    home_score: int
    away_score: int
    status: str = "FT"

    @field_validator("home_score", "away_score")
    @classmethod
    def _score_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("score cannot be negative")
        return value


class EventRecord(BaseModel):
    fixture_id: str
    minute: int
    team: str
    type: str
    player: Optional[str] = None


class LineupRecord(BaseModel):
    fixture_id: str
    team: str
    players: list[str]


class OddsRecord(BaseModel):
    fixture_id: str
    market: str
    outcome: str
    odds: float
    provider: Optional[str] = None
    captured_at: Optional[datetime] = None


class Provider(Protocol):
    meta: ProviderMetadata

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        ...

    def get_results(self) -> Iterable[ResultRecord]:
        ...

    def get_live_events(self) -> Iterable[EventRecord]:
        return []

    def get_lineups(self) -> Iterable[LineupRecord]:
        return []

    def get_odds(self) -> Optional[Iterable[OddsRecord]]:
        return None
