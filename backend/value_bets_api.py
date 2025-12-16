from typing import List

from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .snapshot_service import latest_snapshot_payload
from fastapi import APIRouter

from .live_state import live_state
from .prediction_engine import compute_value_bets

router = APIRouter(prefix="/value-bets", tags=["value-bets"])


@router.get("", dependencies=[Depends(require_user)])
async def list_value_bets() -> List[dict]:
    """Return simplified value bet rows expected by the desktop client."""
    snapshot = latest_snapshot_payload() or live_state.snapshot()
    return compute_value_bets(snapshot)
@router.get("")
async def list_value_bets() -> List[dict]:
    """Return simplified value bet rows expected by the desktop client."""
    snapshot = live_state.snapshot()
    return compute_value_bets(snapshot)

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
