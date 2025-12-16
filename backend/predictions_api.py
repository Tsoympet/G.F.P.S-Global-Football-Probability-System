from typing import List

from fastapi import APIRouter

from .live_state import live_state

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("")
async def list_predictions() -> List[dict]:
    """Return demo-friendly predictions aligned to the desktop type.

    For now we generate simple probabilities from the current fixture snapshot.
    """
    snapshot = live_state.snapshot()
    predictions = []
    for fx in snapshot["fixtures"]:
        predictions.append(
            {
                "fixtureId": fx["id"],
                "homeWinProbability": 0.45,
                "drawProbability": 0.28,
                "awayWinProbability": 0.27,
            }
        )
    return predictions
