from fastapi import APIRouter, Depends, Query

from .auth_dependency import require_user
from .live_state import live_state
from .snapshot_service import latest_snapshot_payload
from .xg import compute_xg_summary

router = APIRouter(prefix="/xg", tags=["xg"])


@router.get("/summary", dependencies=[Depends(require_user)])
async def xg_summary(fixture_id: str | None = Query(None)) -> dict:
    snapshot = latest_snapshot_payload() or live_state.snapshot()
    data = compute_xg_summary(snapshot, fixture_id=fixture_id)
    return {"items": data}
