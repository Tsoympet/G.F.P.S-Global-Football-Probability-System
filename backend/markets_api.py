"""
Markets API Module

⚠️ WARNING: This module uses API-Football, an EXPENSIVE premium API ($50-300/month)
⚠️ GFPS works perfectly fine WITHOUT market data - predictions use model-derived odds
⚠️ You can also use the web scraper to get market data from public sources for FREE

For FREE operation (RECOMMENDED):
- Leave APIFOOTBALL_KEY empty in your .env file
- Use model-derived fair odds instead
- See docs/FREE_OPERATION_GUIDE.md for details
"""

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException

from .auth_dependency import require_user
from .validation import require_decimal_odds

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

router = APIRouter(prefix="/fixtures", tags=["markets"])


async def fetch_api_football(endpoint: str, params: dict) -> dict:
    if not APIFOOTBALL_KEY:
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


@router.get("/markets", dependencies=[Depends(require_user)])
async def fixture_markets(fixture_id: int):
    if not APIFOOTBALL_KEY:
        return {"ok": True, "markets": []}

    try:
        data = await fetch_api_football("odds", {"fixture": fixture_id})
    except Exception as e:
        raise HTTPException(502, f"Upstream error: {e}")

    markets_out = []

    for resp in data.get("response", []):
        for book in resp.get("bookmakers", []):
            bname = book.get("name", "UnknownBook")
            for m in book.get("bets", []):
                market_name = m.get("name", "Unknown")
                selections = []
                for v in m.get("values", []):
                    try:
                        price = require_decimal_odds(float(v.get("odd") or 0), "market")
                    except ValueError:
                        continue
                    selections.append({"outcome": v.get("value"), "odds": price})
                markets_out.append(
                    {
                        "bookmaker": bname,
                        "market": market_name,
                        "selections": selections,
                    }
                )

    return {"ok": True, "markets": markets_out}
