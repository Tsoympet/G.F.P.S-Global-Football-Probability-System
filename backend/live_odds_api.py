import os
from typing import Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException


APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

router = APIRouter(prefix="/live-odds", tags=["live-odds"])

# Lazy import to avoid circular references when the live_state pulls odds snapshots
from .auth_dependency import require_user
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


def _collect_market_lines(
    fixture_id: str, bet_name: str, values: List[Dict], source: str
) -> List[Dict]:
    lines: List[Dict] = []
    lower = (bet_name or "").lower()
    totals: Dict[str, Dict[str, float]] = {}
    handicaps: Dict[str, Dict[str, float]] = {}

    for v in values:
        outcome = (v.get("value") or "").lower()
        price = float(v.get("odd") or 0)
        if lower in {"over/under", "over under", "total goals"} or outcome.startswith("over") or outcome.startswith("under"):
            parts = outcome.split()
            line = parts[1] if len(parts) > 1 else "2.5"
            totals.setdefault(line, {})
            if outcome.startswith("over"):
                totals[line]["over"] = price
            elif outcome.startswith("under"):
                totals[line]["under"] = price
        if "handicap" in lower or outcome.startswith("home") or outcome.startswith("away"):
            parts = outcome.split()
            if len(parts) >= 2:
                side, line = parts[0], parts[1]
                handicaps.setdefault(line, {})
                if side in {"home", "1"}:
                    handicaps[line]["home"] = price
                if side in {"away", "2"}:
                    handicaps[line]["away"] = price

    for line, data in totals.items():
        lines.append(
            {
                "fixtureId": fixture_id,
                "label": f"Total {line}",
                "type": "total",
                "line": line,
                "over": data.get("over"),
                "under": data.get("under"),
                "source": source,
            }
        )

    for line, data in handicaps.items():
        lines.append(
            {
                "fixtureId": fixture_id,
                "label": f"Handicap {line}",
                "type": "handicap",
                "line": line,
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

    # Demo payload mirrors the desktop type definition
    if not APIFOOTBALL_KEY:
        demo_rows = [
            {"market": "Demo FC vs Sample United", "home": 1.95, "draw": 3.30, "away": 4.10, "source": "DemoBook"},
            {"market": "Example Town vs Placeholder City", "home": 2.20, "draw": 3.10, "away": 3.60, "source": "DemoBook"},
        ]
        markets = {
            "1": [
                {"fixtureId": "1", "label": "Total 2.5", "line": "2.5", "type": "total", "over": 1.9, "under": 1.85, "source": "DemoBook"},
                {"fixtureId": "1", "label": "Handicap -1.0", "line": "-1.0", "type": "handicap", "home": 2.15, "away": 1.76, "source": "DemoBook"},
            ],
            "2": [
                {"fixtureId": "2", "label": "Total 3.5", "line": "3.5", "type": "total", "over": 2.4, "under": 1.55, "source": "DemoBook"},
            ],
        }
        await live_state.set_odds(demo_rows)
        await live_state.set_markets(markets)
        return {"outrights": demo_rows, "markets": markets}

    try:
        data = await _fetch_api_football("odds/live", {})
    except Exception as e:
        raise HTTPException(502, f"Upstream error: {e}")

    rows = []
    for resp in data.get("response", []):
        fixture = resp.get("fixture", {})
        fixture_id = str(fixture.get("id"))
        match_label = f"{fixture.get('teams', {}).get('home', {}).get('name', 'Home')} vs {fixture.get('teams', {}).get('away', {}).get('name', 'Away')}"
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
                                "market": match_label,
                                "home": prices["home"],
                                "draw": prices["draw"],
                                "away": prices["away"],
                                "source": source,
                            }
                        )
                extra_lines = _collect_market_lines(fixture_id, bet_name, values, source)
                if extra_lines:
                    markets.setdefault(fixture_id, []).extend(extra_lines)

    await live_state.set_odds(rows)
    if markets:
        await live_state.set_markets(markets)

    return {"outrights": rows, "markets": markets}
