import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException

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


@router.get("/markets")
async def fixture_markets(fixture_id: int):
    if not APIFOOTBALL_KEY:
        # demo markets
        return {
            "ok": True,
            "markets": [
                {
                    "bookmaker": "DemoBook",
                    "market": "1X2",
                    "selections": [
                        {"outcome": "1", "odds": 1.90},
                        {"outcome": "X", "odds": 3.50},
                        {"outcome": "2", "odds": 4.00},
                    ],
                },
                {
                    "bookmaker": "DemoBook",
                    "market": "Over/Under 2.5",
                    "selections": [
                        {"outcome": "Over 2.5", "odds": 2.00},
                        {"outcome": "Under 2.5", "odds": 1.80},
                    ],
                },
                {
                    "bookmaker": "DemoBook",
                    "market": "Both Teams To Score",
                    "selections": [
                        {"outcome": "GG", "odds": 1.85},
                        {"outcome": "NG", "odds": 1.95},
                    ],
                },
            ],
        }

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
                    selections.append(
                        {
                            "outcome": v.get("value"),
                            "odds": float(v.get("odd") or 0),
                        }
                    )
                markets_out.append(
                    {
                        "bookmaker": bname,
                        "market": market_name,
                        "selections": selections,
                    }
                )

    return {"ok": True, "markets": markets_out}
