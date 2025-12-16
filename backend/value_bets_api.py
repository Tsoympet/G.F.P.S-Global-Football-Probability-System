from typing import List

from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .snapshot_service import latest_snapshot_payload
from .prediction_engine import compute_value_bets

router = APIRouter(prefix="/value-bets", tags=["value-bets"])


@router.get("", dependencies=[Depends(require_user)])
async def list_value_bets() -> List[dict]:
    """Return simplified value bet rows expected by the desktop client."""
    snapshot = latest_snapshot_payload() or live_state.snapshot()
    return compute_value_bets(snapshot)
