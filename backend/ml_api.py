import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .db import SessionLocal
from .models import ModelActivation, ModelArtifact, ModelVersion
from .ml_trainer import queue_training
from .auth_dependency import require_user

router = APIRouter(prefix="/ml", tags=["ml"])
logger = logging.getLogger("gfps.ml")


def _sanitize_for_log(value: Optional[str]) -> Optional[str]:
    """
    Remove newline characters from values before logging to reduce
    the risk of log injection when logging user-controlled data.
    """
    if value is None:
        return None
    return value.replace("\r", "").replace("\n", "")


def _ensure_seed_model() -> None:
    with SessionLocal() as db:
        if db.query(ModelVersion).count() == 0:
            seed = ModelVersion(
                version="v1",
                status="active",
                metrics={"roi": 0.08, "logLoss": 0.55},
                activated_at=datetime.now(timezone.utc),
            )
            db.add(seed)
            db.commit()


class ArtifactRequest(BaseModel):
    version: str
    uri: str
    checksum: Optional[str] = None
    meta: Optional[dict] = None


class ActivationRequest(BaseModel):
    activatedBy: Optional[str] = None
    reason: Optional[str] = None


class RollbackRequest(BaseModel):
    toVersion: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None


def _latest_artifact_map(db) -> Dict[str, ModelArtifact]:
    artifacts = (
        db.query(ModelArtifact)
        .order_by(ModelArtifact.version, ModelArtifact.created_at.desc())
        .all()
    )
    mapping: Dict[str, ModelArtifact] = {}
    for art in artifacts:
        mapping.setdefault(art.version, art)
    return mapping


def _activate_version(
    version: str, activated_by: Optional[str] = None, reason: Optional[str] = None, rollback_of: Optional[str] = None
) -> ModelActivation:
    _ensure_seed_model()
    with SessionLocal() as db:
        target = db.query(ModelVersion).filter(ModelVersion.version == version).first()
        if not target:
            raise HTTPException(404, f"Model {version} not found")

        prev_active = (
            db.query(ModelVersion)
            .filter(ModelVersion.status == "active")
            .order_by(ModelVersion.activated_at.desc())
            .first()
        )
        previous_version = prev_active.version if prev_active else None
        active_total = db.query(ModelVersion).filter(ModelVersion.status == "active").count()
        if active_total > 1:
            logger.error(
                "Multiple active models detected during activation",
                extra={"count": active_total, "target": _sanitize_for_log(version)},
            )
            raise HTTPException(409, "Multiple active models detected; activation aborted")

        now = datetime.now(timezone.utc)
        target.status = "active"
        target.activated_at = now
        db.add(target)

        deactivated = db.query(ModelVersion).filter(
            ModelVersion.version != version, ModelVersion.status == "active"
        ).update({"status": "ready", "activated_at": None})

        activation = ModelActivation(
            version=version,
            previous_version=previous_version,
            activated_by=activated_by,
            reason=reason,
            rollback_of=rollback_of,
        )
        db.add(activation)
        db.commit()
        db.refresh(activation)
        return activation


@router.post("/train", dependencies=[Depends(require_user)])
async def train_model():
    """Kick off a background training job and return its run id."""

    _ensure_seed_model()
    with SessionLocal() as db:
        latest = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).first()
        next_version = f"v{latest.id + 1}" if latest else "v1"

    run_id = queue_training(asyncio.get_running_loop(), next_version)
    return {"message": f"Training started for {next_version}", "runId": run_id}


@router.get("/models", dependencies=[Depends(require_user)])
async def list_models() -> List[dict]:
    """Return persisted model metadata for desktop diagnostics."""

    _ensure_seed_model()
    with SessionLocal() as db:
        models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
        artifacts = _latest_artifact_map(db)
        return [
            {
                "version": m.version,
                "roi": (m.metrics or {}).get("roi", 0.0),
                "logLoss": (m.metrics or {}).get("logLoss", 1.0),
                "status": m.status,
                "artifact": (
                    {
                        "uri": artifacts[m.version].uri,
                        "checksum": artifacts[m.version].checksum,
                    }
                    if m.version in artifacts
                    else None
                ),
            }
            for m in models
        ]


@router.get("/activations", dependencies=[Depends(require_user)])
async def activation_history() -> List[dict]:
    with SessionLocal() as db:
        rows = db.query(ModelActivation).order_by(ModelActivation.created_at.desc()).all()
        return [
            {
                "version": row.version,
                "previous": row.previous_version,
                "activatedBy": row.activated_by,
                "reason": row.reason,
                "rollbackOf": row.rollback_of,
                "activatedAt": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]


@router.post("/activate/{version}", dependencies=[Depends(require_user)])
async def activate_model(version: str, req: Optional[ActivationRequest] = None):
    """Activate a model version and demote any previously active entries."""

    payload = req or ActivationRequest()
    activation = _activate_version(version, activated_by=payload.activatedBy, reason=payload.reason)
    return {"message": f"Activated model {version}", "activationId": activation.id}


@router.post("/rollback", dependencies=[Depends(require_user)])
async def rollback_model(req: RollbackRequest):
    """Rollback to a previously active model using the activation log."""

    _ensure_seed_model()
    with SessionLocal() as db:
        if req.toVersion:
            target_version = req.toVersion
        else:
            last_activation = (
                db.query(ModelActivation).order_by(ModelActivation.created_at.desc()).first()
            )
            target_version = last_activation.previous_version if last_activation else None
        active = (
            db.query(ModelVersion)
            .filter(ModelVersion.status == "active")
            .order_by(ModelVersion.activated_at.desc())
            .first()
        )

    if not target_version:
        raise HTTPException(400, "No previous activation to rollback to")

    activation = _activate_version(
        target_version,
        activated_by=req.actor,
        reason=req.reason or "rollback",
        rollback_of=active.version if active else None,
    )
    return {"message": f"Rolled back to {target_version}", "activationId": activation.id}


@router.post("/artifacts", dependencies=[Depends(require_user)])
async def register_artifact(req: ArtifactRequest):
    """Store model artifact metadata for reproducibility."""

    with SessionLocal() as db:
        artifact = ModelArtifact(
            version=req.version,
            uri=req.uri,
            checksum=req.checksum,
            meta=req.meta,
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return {"ok": True, "artifactId": artifact.id}


@router.get("/artifacts", dependencies=[Depends(require_user)])
async def list_artifacts() -> List[dict]:
    with SessionLocal() as db:
        rows = db.query(ModelArtifact).order_by(ModelArtifact.created_at.desc()).all()
        return [
            {
                "id": row.id,
                "version": row.version,
                "uri": row.uri,
                "checksum": row.checksum,
                "meta": row.meta,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
