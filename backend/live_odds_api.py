import os
from typing import Dict, List

import httpx
from fastapi import APIRouter, HTTPException


APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

router = APIRouter(prefix="/live-odds", tags=["live-odds"])

# Lazy import to avoid circular references when the live_state pulls odds snapshots
from .live_state import live_state  # noqa: E402


async def _fetch_api_football(endpoint: str, params: Dict) -> Dict:
    """Lightweight wrapper around the API Football client.

    We keep it minimal here because this endpoint is currently used only to
    provide demo-compatible odds rows for the desktop client.
    """

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


def _extract_match_winner_prices(values: List[Dict]) -> Dict[str, float]:
    """Normalize API Football odds values into home/draw/away selections."""

    prices: Dict[str, float] = {}
    for v in values:
        outcome = (v.get("value") or "").lower()
        if outcome in {"home", "1"}:
            prices["home"] = float(v.get("odd") or 0)
        elif outcome in {"draw", "x"}:
            prices["draw"] = float(v.get("odd") or 0)
        elif outcome in {"away", "2"}:
            prices["away"] = float(v.get("odd") or 0)
    return prices


@router.get("")
async def list_live_odds():
    """Return simplified live odds rows for the desktop LiveMatchCenter."""

    # Demo payload mirrors the desktop type definition
    if not APIFOOTBALL_KEY:
        demo_rows = [
            {"market": "Demo FC vs Sample United", "home": 1.95, "draw": 3.30, "away": 4.10, "source": "DemoBook"},
            {"market": "Example Town vs Placeholder City", "home": 2.20, "draw": 3.10, "away": 3.60, "source": "DemoBook"},
        ]
        await live_state.set_odds(demo_rows)
        return demo_rows

    try:
        data = await _fetch_api_football("odds/live", {})
    except Exception as e:
        raise HTTPException(502, f"Upstream error: {e}")

    rows = []
    for resp in data.get("response", []):
        fixture = resp.get("fixture", {})
        match_label = f"{fixture.get('teams', {}).get('home', {}).get('name', 'Home')} vs {fixture.get('teams', {}).get('away', {}).get('name', 'Away')}"
        for bookmaker in resp.get("bookmakers", []):
            source = bookmaker.get("name")
            for bet in bookmaker.get("bets", []):
                if (bet.get("name") or "").lower() not in {"match winner", "1x2"}:
                    continue
                prices = _extract_match_winner_prices(bet.get("values", []))
                if {"home", "draw", "away"} <= set(prices):
                    rows.append(
                        {
                            "market": match_label,
                            "home": prices["home"],
                            "draw": prices["draw"],
                            "away": prices["away"],
                            "source": source,
                        }
                    )

    await live_state.set_odds(rows)

    return rows
