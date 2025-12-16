import asyncio
import os
from typing import List

import httpx

from ..fixtures_api import _map_status

from ..live_state import live_state


STREAMER_ENABLED = os.getenv("STREAMER_ENABLED", "false").lower() in ("1", "true", "yes")
STREAMER_INTERVAL_SEC = int(os.getenv("STREAMER_INTERVAL_SEC", "15"))
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")


async def _fetch_live_fixtures() -> List[dict]:
    """Poll API Football for live fixtures and normalize to the client shape."""

    if not APIFOOTBALL_KEY:
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

        fixtures.append(
            {
                "id": str(fixture.get("id")),
                "league": league.get("name"),
                "homeTeam": teams.get("home", {}).get("name"),
                "awayTeam": teams.get("away", {}).get("name"),
                "startTime": fixture.get("date"),
                "status": status,
                "timer": timer,
                "score": score,
            }
        )

    return fixtures


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
                # fall back to demo heartbeat so websocket clients still tick
                await live_state.tick_demo_clock()
            await live_state.tick_demo_clock()
        except Exception as e:
            print("[streamer] ERROR:", e)
        await asyncio.sleep(STREAMER_INTERVAL_SEC)


def start_streamer_background(loop: asyncio.AbstractEventLoop):
    if not STREAMER_ENABLED:
        return
    loop.create_task(live_streamer_loop())
