import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from .db import SessionLocal
from .models import ModelVersion
from .ml_trainer import queue_training

router = APIRouter(prefix="/ml", tags=["ml"])


def _ensure_seed_model() -> None:
    with SessionLocal() as db:
        if db.query(ModelVersion).count() == 0:
            seed = ModelVersion(
                version="v1",
                status="active",
                metrics={"roi": 0.08, "logLoss": 0.55},
                activated_at=datetime.utcnow(),
            )
            db.add(seed)
            db.commit()


@router.post("/train")
async def train_model():
    """Kick off a background training job and return its run id."""

    _ensure_seed_model()
    with SessionLocal() as db:
        latest = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).first()
        next_version = f"v{latest.id + 1}" if latest else "v1"

    run_id = queue_training(asyncio.get_event_loop(), next_version)
    return {"message": f"Training started for {next_version}", "runId": run_id}


@router.get("/models")
async def list_models() -> List[dict]:
    """Return persisted model metadata for desktop diagnostics."""

    _ensure_seed_model()
    with SessionLocal() as db:
        models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
        return [
            {
                "version": m.version,
                "roi": (m.metrics or {}).get("roi", 0.0),
                "logLoss": (m.metrics or {}).get("logLoss", 1.0),
                "status": m.status,
            }
            for m in models
        ]


@router.post("/activate/{version}")
async def activate_model(version: str):
    """Activate a model version and demote any previously active entries."""

    _ensure_seed_model()
    with SessionLocal() as db:
        target = db.query(ModelVersion).filter(ModelVersion.version == version).first()
        if not target:
            raise HTTPException(404, f"Model {version} not found")

        now = datetime.utcnow()
        target.status = "active"
        target.activated_at = now
        db.add(target)

        db.query(ModelVersion).filter(
            ModelVersion.version != version, ModelVersion.status == "active"
        ).update({"status": "ready", "activated_at": None})

        db.commit()

    return {"message": f"Activated model {version}"}
