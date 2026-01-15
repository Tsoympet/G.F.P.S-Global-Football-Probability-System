from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .live_state import live_state
from .prediction_engine import EV_MIN_THRESHOLD, MODEL_VERSION, generate_predictions
from .snapshot_service import SNAPSHOT_INTERVAL_SEC, latest_snapshot_summary
from .streamer.live_streamer import STREAMER_ENABLED
from .alert_engine import ALERT_ENGINE_ENABLED

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


def _fallback_snapshot() -> dict:
    snapshot = live_state.snapshot()
    markets = snapshot.get("markets") or {}
    predictions = generate_predictions(snapshot)
    return {
        "snapshotId": None,
        "reason": "memory",
        "capturedAt": None,
        "ageSec": None,
        "fixtureCount": len(snapshot.get("fixtures") or []),
        "oddsCount": len(snapshot.get("odds") or []),
        "marketLineCount": sum(len(lines) for lines in markets.values()),
        "predictionCount": len(predictions),
        "valueBetCount": 0,
        "modelVersion": MODEL_VERSION,
    }


@router.get("/status", dependencies=[Depends(require_user)])
async def pipeline_status() -> dict:
    snapshot = latest_snapshot_summary() or _fallback_snapshot()
    return {
        "ok": True,
        "snapshot": snapshot,
        "model": {"version": snapshot.get("modelVersion", MODEL_VERSION), "evThreshold": EV_MIN_THRESHOLD},
        "pipeline": {
            "streamerEnabled": STREAMER_ENABLED,
            "alertEngineEnabled": ALERT_ENGINE_ENABLED,
            "snapshotIntervalSec": SNAPSHOT_INTERVAL_SEC,
        },
    }
