"""
Live Odds API Module

⚠️ WARNING: This module uses API-Football, an EXPENSIVE premium API ($50-300/month)
⚠️ GFPS works perfectly fine WITHOUT this API using FREE alternatives
⚠️ Only use this if you already have an API-Football subscription

For FREE operation:
- Leave APIFOOTBALL_KEY empty in your .env file
- Use model-derived fair odds instead of market odds
- Use the web scraper for publicly available odds
- See docs/FREE_OPERATION_GUIDE.md for details
"""

import os
from typing import Dict, List

import httpx
from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .validation import parse_iso_datetime, parse_market_line, require_decimal_odds

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

router = APIRouter(prefix="/live-odds", tags=["live-odds"])


async def _fetch_api_football(endpoint: str, params: Dict) -> Dict:
    """
    Lightweight wrapper around the API Football client.
    
    ⚠️ WARNING: API-Football is an EXPENSIVE premium service ($50-300/month)
    This function returns empty results when APIFOOTBALL_KEY is not set.
    GFPS works perfectly fine without this - use FREE data providers instead.
    """

    if not APIFOOTBALL_KEY:
        # No premium API key - return empty results (RECOMMENDED for cost savings)
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
        try:
            price = require_decimal_odds(float(v.get("odd") or 0), outcome or "odds")
        except ValueError:
            continue
        if outcome in {"home", "1"}:
            prices["home"] = price
        elif outcome in {"draw", "x"}:
            prices["draw"] = price
        elif outcome in {"away", "2"}:
            prices["away"] = price
    return prices


def _collect_market_lines(
    fixture_id: str, bet_name: str, values: List[Dict], source: str
) -> List[Dict]:
    lines: List[Dict] = []
    lower = (bet_name or "").lower()
    totals: Dict[str, Dict[str, float]] = {}
    handicaps: Dict[str, Dict[str, float]] = {}

    for v in values:
        outcome = (v.get("value") or "").lower()
        try:
            price = require_decimal_odds(float(v.get("odd") or 0), outcome or "odds")
        except ValueError:
            continue
        if lower in {"over/under", "over under", "total goals"} or outcome.startswith(
            "over"
        ) or outcome.startswith("under"):
            parts = outcome.split()
            line = parts[1] if len(parts) > 1 else "2.5"
            totals.setdefault(line, {})
            if outcome.startswith("over"):
                totals[line]["over"] = price
            elif outcome.startswith("under"):
                totals[line]["under"] = price
        if "handicap" in lower or outcome.startswith("home") or outcome.startswith(
            "away"
        ):
            parts = outcome.split()
            if len(parts) >= 2:
                side, line = parts[0], parts[1]
                handicaps.setdefault(line, {})
                if side in {"home", "1"}:
                    handicaps[line]["home"] = price
                if side in {"away", "2"}:
                    handicaps[line]["away"] = price

    for line, data in totals.items():
        try:
            parsed_line = parse_market_line(line)
        except ValueError:
            continue
        lines.append(
            {
                "fixtureId": fixture_id,
                "label": f"Total {parsed_line}",
                "type": "total",
                "line": str(parsed_line),
                "over": data.get("over"),
                "under": data.get("under"),
                "source": source,
            }
        )

    for line, data in handicaps.items():
        try:
            parsed_line = parse_market_line(line)
        except ValueError:
            continue
        lines.append(
            {
                "fixtureId": fixture_id,
                "label": f"Handicap {parsed_line}",
                "type": "handicap",
                "line": str(parsed_line),
                "home": data.get("home"),
                "away": data.get("away"),
                "source": source,
            }
        )

    return lines


@router.get("", dependencies=[Depends(require_user)])
async def list_live_odds():
    """Return simplified live odds rows + alternative markets."""

    markets: Dict[str, List[Dict]] = {}
    rows: List[Dict] = []

    if not APIFOOTBALL_KEY:
        snapshot = live_state.snapshot()
        return {"outrights": snapshot["odds"], "markets": snapshot["markets"]}

    data = await _fetch_api_football("odds/live", params={"page": 1})

    for resp in data.get("response", []):
        fixture = resp.get("fixture", {})
        fixture_id = str(fixture.get("id"))
        if not fixture_id or fixture_id == "None":
            continue
        try:
            start_time = parse_iso_datetime(fixture.get("date") or "")
        except ValueError:
            continue
        home_name = fixture.get("teams", {}).get("home", {}).get("name")
        away_name = fixture.get("teams", {}).get("away", {}).get("name")
        if not home_name or not away_name:
            continue
        match_label = f"{home_name} vs {away_name}"
        for bookmaker in resp.get("bookmakers", []):
            source = bookmaker.get("name")
            for bet in bookmaker.get("bets", []):
                bet_name = bet.get("name") or ""
                values = bet.get("values", [])
                if bet_name.lower() in {"match winner", "1x2"}:
                    prices = _extract_match_winner_prices(values)
                    if {"home", "draw", "away"} <= set(prices):
                        rows.append(
                            {
                                "fixtureId": fixture_id,
                                "market": match_label,
                                "home": prices["home"],
                                "draw": prices["draw"],
                                "away": prices["away"],
                                "source": source,
                                "startTime": start_time,
                            }
                        )
                extra_lines = _collect_market_lines(
                    fixture_id, bet_name, values, source
                )
                if extra_lines:
                    markets.setdefault(fixture_id, []).extend(extra_lines)

    await live_state.set_odds(rows)
    await live_state.set_markets(markets)

    return {"outrights": rows, "markets": markets}
