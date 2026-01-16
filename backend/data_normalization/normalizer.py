from __future__ import annotations

import hashlib
import unicodedata
from datetime import datetime, timezone
from typing import Mapping, MutableMapping

from ..data_providers.base import FixtureRecord

TEAM_ALIASES: Mapping[str, str] = {
    "man utd": "Manchester United",
    "manchester u.": "Manchester United",
    "man city": "Manchester City",
    "spurs": "Tottenham Hotspur",
    "liverpool fc": "Liverpool",
}

LEAGUE_ALIASES: Mapping[str, str] = {
    "epl": "Premier League",
    "premier league": "Premier League",
    "english premier league": "Premier League",
}


def _clean(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).strip()
    return value


def normalize_team_name(name: str) -> str:
    key = _clean(name).lower()
    return TEAM_ALIASES.get(key, _clean(name))


def normalize_league(league: str) -> str:
    key = _clean(league).lower()
    return LEAGUE_ALIASES.get(key, _clean(league))


def normalize_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def stable_fixture_id(record: FixtureRecord) -> str:
    base = f"{normalize_league(record.league)}-{record.season}-{normalize_team_name(record.home_team)}-{normalize_team_name(record.away_team)}-{record.kickoff.date().isoformat()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def normalize_fixture(record: FixtureRecord) -> FixtureRecord:
    data: MutableMapping = record.model_dump()
    data["home_team"] = normalize_team_name(record.home_team)
    data["away_team"] = normalize_team_name(record.away_team)
    data["league"] = normalize_league(record.league)
    data["kickoff"] = normalize_timezone(record.kickoff)
    if not record.fixture_id:
        data["fixture_id"] = stable_fixture_id(record)
    return FixtureRecord(**data)
