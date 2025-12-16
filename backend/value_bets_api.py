from typing import List

from fastapi import APIRouter

from .live_state import live_state

router = APIRouter(prefix="/value-bets", tags=["value-bets"])


@router.get("")
async def list_value_bets() -> List[dict]:
    """Return simplified value bet rows expected by the desktop client."""

    bets: List[dict] = []
    snapshot = live_state.snapshot()
    for fx in snapshot["fixtures"]:
        match_label = f"{fx['homeTeam']} vs {fx['awayTeam']}"
        # Demo model probability and odds
        model_prob = 0.55
        odds = 2.2
        expected_value = model_prob * odds - 1
        bets.append(
            {
                "match": match_label,
                "market": "Match Winner - Home",
                "odds": odds,
                "modelProbability": model_prob,
                "expectedValue": round(expected_value, 2),
            }
        )
    return bets
