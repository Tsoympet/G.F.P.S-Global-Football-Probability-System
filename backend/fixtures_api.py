import os
from datetime import date
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException

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


@router.get("")
async def list_fixtures(league_id: Optional[int] = None, date_str: Optional[str] = None):
    if not date_str:
        d = date.today().isoformat()
    else:
        d = date_str

    if not APIFOOTBALL_KEY:
        # simple demo fixture
        return {
            "ok": True,
            "fixtures": [
                {
                    "fixture_id": 1,
                    "league_id": league_id or 39,
                    "league": "Premier League",
                    "home": "Demo FC",
                    "away": "Sample United",
                    "kickoff": f"{d}T15:00:00Z",
                }
            ],
        }

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
        fixtures.append(
            {
                "fixture_id": f["id"],
                "league_id": l["id"],
                "league": l["name"],
                "home": h["name"],
                "away": a["name"],
                "kickoff": f["date"],
            }
        )
    return {"ok": True, "fixtures": fixtures}
