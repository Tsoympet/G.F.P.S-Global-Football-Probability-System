import os
from datetime import date
from typing import Optional, Tuple

import httpx
from fastapi import APIRouter, HTTPException

from .live_state import live_state

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

router = APIRouter(prefix="/fixtures", tags=["fixtures"])


async def fetch_api_football(endpoint: str, params: dict) -> dict:
    if not APIFOOTBALL_KEY:
        # demo fallback
        return {"response": []}
    headers = {"x-apisports-key": APIFOOTBALL_KEY}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"https://v3.football.api-sports.io/{endpoint}",
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        return r.json()



def _map_status(short_code: str, elapsed: Optional[int]) -> Tuple[str, Optional[str]]:
    live_codes = {"1H", "2H", "ET", "HT"}
    finished_codes = {"FT", "AET", "PEN"}

    if short_code in live_codes:
        timer = f"{elapsed}'" if elapsed is not None else None
        return "live", timer
    if short_code in finished_codes:
        return "finished", None
    return "scheduled", None


@router.get("")
async def list_fixtures(league_id: Optional[int] = None, date_str: Optional[str] = None):
    if not date_str:
        d = date.today().isoformat()
    else:
        d = date_str

    if not APIFOOTBALL_KEY:
        return live_state.snapshot()["fixtures"]

    params = {"date": d}
    if league_id:
        params["league"] = league_id
        params["season"] = 2024

    try:
        data = await fetch_api_football("fixtures", params)
    except Exception as e:
        raise HTTPException(502, f"Upstream error: {e}")

    fixtures = []
    for item in data.get("response", []):
        f = item["fixture"]
        l = item["league"]
        h = item["teams"]["home"]
        a = item["teams"]["away"]
        status, timer = _map_status(f.get("status", {}).get("short", ""), f.get("status", {}).get("elapsed"))
        goals = item.get("goals", {})
        score = None
        if goals.get("home") is not None and goals.get("away") is not None:
            score = {"home": goals["home"], "away": goals["away"]}

        fixtures.append(
            {
                "id": str(f["id"]),
                "league": l["name"],
                "homeTeam": h["name"],
                "awayTeam": a["name"],
                "startTime": f["date"],
                "status": status,
                "timer": timer,
                "score": score,
            }
        )
    # Update live snapshot for downstream consumers (WebSocket, predictions, EV)
    await live_state.set_fixtures(fixtures)
    return fixtures
