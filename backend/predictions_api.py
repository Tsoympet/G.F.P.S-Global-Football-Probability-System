from typing import List

from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .snapshot_service import latest_snapshot_payload
from .prediction_engine import generate_predictions

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", dependencies=[Depends(require_user)])
async def list_predictions() -> List[dict]:
    """Return demo-friendly predictions aligned to the desktop type.

    For now we generate simple probabilities from the current fixture snapshot.
    """
    snapshot = latest_snapshot_payload() or live_state.snapshot()
    return generate_predictions(snapshot)
