from typing import List

from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .prediction_engine import generate_predictions
from .snapshot_service import latest_snapshot_payload

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", dependencies=[Depends(require_user)])
async def list_predictions() -> List[dict]:
    """Return predictions aligned to the desktop type."""

    snapshot = latest_snapshot_payload() or live_state.snapshot()
    return generate_predictions(snapshot)
