"""
Live Streamer Module

⚠️ WARNING: This module uses API-Football, an EXPENSIVE premium API ($50-300/month)
⚠️ Live streaming works with FREE alternatives too (OpenLigaDB for German leagues)
⚠️ Consider disabling this unless you have an API-Football subscription

For FREE operation (RECOMMENDED):
- Set STREAMER_ENABLED=false in your .env file (default)
- Leave APIFOOTBALL_KEY empty
- Use ENABLE_OPENLIGADB=1 for free live scores
- See docs/FREE_OPERATION_GUIDE.md for details
"""

import asyncio
import os
from typing import List

import httpx

from ..fixtures_api import _map_status

from ..live_state import live_state
from ..validation import parse_iso_datetime


STREAMER_ENABLED = os.getenv("STREAMER_ENABLED", "false").lower() in ("1", "true", "yes")
STREAMER_INTERVAL_SEC = int(os.getenv("STREAMER_INTERVAL_SEC", "15"))
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")


async def _fetch_live_fixtures() -> List[dict]:
    """
    Poll API Football for live fixtures and normalize to the client shape.
    
    ⚠️ NOTE: This uses the EXPENSIVE API-Football service.
    Returns empty list when APIFOOTBALL_KEY is not set (RECOMMENDED for cost savings).
    """

    if not APIFOOTBALL_KEY:
        # No premium API key - return empty list (RECOMMENDED for cost savings)
        return []

    headers = {"x-apisports-key": APIFOOTBALL_KEY}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://v3.football.api-sports.io/fixtures",
            headers=headers,
            params={"live": "all"},
        )
        resp.raise_for_status()
        data = resp.json()

    fixtures = []
    for item in data.get("response", []):
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})
        status, timer = _map_status(
            fixture.get("status", {}).get("short", ""),
            fixture.get("status", {}).get("elapsed"),
        )
        goals = item.get("goals", {})
        score = None
        if goals.get("home") is not None and goals.get("away") is not None:
            score = {"home": goals["home"], "away": goals["away"]}

        try:
            start_time = parse_iso_datetime(fixture.get("date") or "")
        except ValueError:
            continue
        fixtures.append(
            {
                "id": str(fixture.get("id")),
                "league": league.get("name"),
                "leagueId": str(league.get("id")) if league.get("id") is not None else None,
                "homeTeam": teams.get("home", {}).get("name"),
                "awayTeam": teams.get("away", {}).get("name"),
                "startTime": start_time,
                "status": status,
                "timer": timer,
                "score": score,
            }
        )

    return fixtures


async def _fetch_fixture_events(fixture_id: str) -> List[dict]:
    if not APIFOOTBALL_KEY:
        return []

    headers = {"x-apisports-key": APIFOOTBALL_KEY}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://v3.football.api-sports.io/fixtures/events",
            headers=headers,
            params={"fixture": fixture_id},
        )
        resp.raise_for_status()
        data = resp.json()

    events: List[dict] = []
    for ev in data.get("response", []):
        minute = ev.get("time", {}).get("elapsed") or 0
        etype = (ev.get("type") or "info").lower()
        detail = ev.get("detail") or ""
        team = ev.get("team", {}).get("name", "")
        player = ev.get("player", {}).get("name")
        assist = ev.get("assist", {}).get("name")
        comments = ev.get("comments")
        description = f"{team}: {detail}".strip()
        payload = {
            "minute": minute,
            "description": description,
            "type": etype,
            "detail": detail,
            "team": team,
            "player": player,
            "assist": assist,
            "comments": comments,
        }
        events.append(payload)
    return events


async def _refresh_live_snapshot() -> bool:
    """Update the shared live snapshot with upstream data.

    Returns True when upstream data was applied, False when no update occurred
    (e.g., missing API key or empty upstream response).
    """

    try:
        fixtures = await _fetch_live_fixtures()
    except Exception as exc:  # pragma: no cover - network errors
        print(f"[streamer] Upstream fetch failed: {exc}")
        return False

    if fixtures:
        await live_state.set_fixtures(fixtures)
        events_by_fixture = {}
        for f in fixtures:
            events_by_fixture[f.get("id", "")] = await _fetch_fixture_events(f.get("id"))
        if any(events_by_fixture.values()):
            await live_state.set_events(events_by_fixture)
        return True

    return False


async def live_streamer_loop():
    if not STREAMER_ENABLED:
        print("[streamer] Disabled via STREAMER_ENABLED")
        return

    print("[streamer] Live streamer started")
    while True:
        try:
            updated = await _refresh_live_snapshot()
            if not updated:
                await live_state.tick_fallback_clock()
        except Exception as e:
            print("[streamer] ERROR:", e)
        await asyncio.sleep(STREAMER_INTERVAL_SEC)


def start_streamer_background(loop: asyncio.AbstractEventLoop):
    if not STREAMER_ENABLED:
        return
    loop.create_task(live_streamer_loop())
