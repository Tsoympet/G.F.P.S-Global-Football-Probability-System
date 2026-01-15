import os
from typing import Dict

from fastapi import APIRouter, Depends

from .auth_dependency import require_user
from .db import SessionLocal
from .models import ModelActivation, ModelVersion
from .snapshot_service import latest_snapshot_summary

router = APIRouter(prefix="/observability", tags=["observability"])

# Threshold defaults are environment-tunable to align with deployment SLAs.
STALE_DATA_THRESHOLD_SEC = int(os.getenv("STALE_DATA_THRESHOLD_SEC", "300"))
PERFORMANCE_LOGLOSS_THRESHOLD = float(os.getenv("PERFORMANCE_LOGLOSS_THRESHOLD", "0.9"))


@router.get("/metrics", dependencies=[Depends(require_user)])
async def observability_metrics() -> Dict[str, object]:
    """Expose lightweight observability metrics for dashboards."""

    snapshot = latest_snapshot_summary()
    with SessionLocal() as db:
        active_model = (
            db.query(ModelVersion)
            .filter(ModelVersion.status == "active")
            .order_by(ModelVersion.activated_at.desc())
            .first()
        )
        last_activation = db.query(ModelActivation).order_by(ModelActivation.created_at.desc()).first()

    model_metrics = (active_model.metrics or {}) if active_model else {}
    return {
        "ok": True,
        "dataFreshnessSec": snapshot.get("ageSec") if snapshot else None,
        "snapshot": snapshot,
        "model": {
            "version": active_model.version if active_model else None,
            "metrics": model_metrics,
            "activatedAt": active_model.activated_at.isoformat() if active_model and active_model.activated_at else None,
        },
        "activation": {
            "current": active_model.version if active_model else None,
            "previous": last_activation.previous_version if last_activation else None,
            "lastChangeAt": last_activation.created_at.isoformat() if last_activation and last_activation.created_at else None,
        },
    }


@router.get("/alerts", dependencies=[Depends(require_user)])
async def observability_alerts() -> Dict[str, object]:
    """Return alert-style signals for dashboards/monitoring."""

    snapshot = latest_snapshot_summary()
    age_sec = snapshot.get("ageSec") if snapshot else None
    stale = age_sec is not None and age_sec > STALE_DATA_THRESHOLD_SEC

    performance_warning = False
    with SessionLocal() as db:
        active_model = (
            db.query(ModelVersion)
            .filter(ModelVersion.status == "active")
            .order_by(ModelVersion.activated_at.desc())
            .first()
        )
        metrics = (active_model.metrics or {}) if active_model else {}
        performance_warning = metrics.get("logLoss", 0.0) > PERFORMANCE_LOGLOSS_THRESHOLD

    return {
        "ok": True,
        "staleData": stale,
        "dataAgeSec": age_sec,
        "performanceWarning": performance_warning,
    }
