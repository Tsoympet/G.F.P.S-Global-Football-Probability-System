from __future__ import annotations

import os
from typing import Optional, Tuple

import httpx
from fastapi import APIRouter, Depends, HTTPException

from .auth_dependency import require_user
from .live_state import live_state
from .validation import parse_date_string, parse_iso_datetime

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
DEFAULT_SEASON = os.getenv("DEFAULT_SEASON", "2024")

router = APIRouter(prefix="/fixtures", tags=["fixtures"])


async def fetch_api_football(endpoint: str, params: dict) -> dict:
    if not APIFOOTBALL_KEY:
        return {"response": []}
    headers = {"x-apisports-key": APIFOOTBALL_KEY}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"https://v3.football.api-sports.io/{endpoint}",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()


def _map_status(short_code: str, elapsed: Optional[int]) -> Tuple[str, Optional[str]]:
    live_codes = {"1H", "2H", "ET", "HT"}
    finished_codes = {"FT", "AET", "PEN"}

    if short_code in live_codes:
        timer = f"{elapsed}'" if elapsed is not None else None
        return "live", timer
    if short_code in finished_codes:
        return "finished", None
    return "scheduled", None


def _normalize_fixture(item: dict) -> Optional[dict]:
    fixture = item.get("fixture") or {}
    league = item.get("league") or {}
    teams = item.get("teams") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    fixture_id = fixture.get("id")
    if not fixture_id or not home.get("name") or not away.get("name"):
        return None
    try:
        start_time = parse_iso_datetime(fixture.get("date") or "")
    except ValueError:
        return None
    status, timer = _map_status(
        fixture.get("status", {}).get("short", ""),
        fixture.get("status", {}).get("elapsed"),
    )
    goals = item.get("goals", {}) or {}
    score = None
    if goals.get("home") is not None and goals.get("away") is not None:
        score = {"home": goals["home"], "away": goals["away"]}

    return {
        "id": str(fixture_id),
        "league": league.get("name") or "Unknown",
        "leagueId": str(league.get("id")) if league.get("id") is not None else None,
        "homeTeam": home.get("name"),
        "awayTeam": away.get("name"),
        "startTime": start_time,
        "status": status,
        "timer": timer,
        "score": score,
    }


@router.get("", dependencies=[Depends(require_user)])
async def list_fixtures(league_id: Optional[int] = None, date_str: Optional[str] = None):
    try:
        query_date = parse_date_string(date_str)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    if not APIFOOTBALL_KEY:
        return live_state.snapshot()["fixtures"]

    params = {"date": query_date}
    if league_id:
        params["league"] = league_id
        params["season"] = DEFAULT_SEASON

    try:
        data = await fetch_api_football("fixtures", params)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Upstream error: {exc}")

    fixtures = []
    for item in data.get("response", []):
        normalized = _normalize_fixture(item)
        if normalized:
            fixtures.append(normalized)

    if data.get("response") and not fixtures:
        raise HTTPException(502, "Upstream data failed validation")

    await live_state.set_fixtures(fixtures)
    return fixtures
