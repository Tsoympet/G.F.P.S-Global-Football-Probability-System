from typing import List

from fastapi import APIRouter

from .live_state import live_state
from .prediction_engine import compute_value_bets

router = APIRouter(prefix="/value-bets", tags=["value-bets"])


@router.get("")
async def list_value_bets() -> List[dict]:
    """Return simplified value bet rows expected by the desktop client."""
    snapshot = live_state.snapshot()
    return compute_value_bets(snapshot)
