from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc

from .auth_dependency import require_user
from .db import SessionLocal
from .models import (
    LiveSnapshotRecord,
    PredictionSnapshotRecord,
    ValueBetSnapshotRecord,
)
from .validation import format_iso_datetime

router = APIRouter(prefix="/replay", tags=["replay"])


def _event_count(payload: Dict) -> int:
    events = payload.get("events") or {}
    return sum(len(rows or []) for rows in events.values())


@router.get("/snapshots", dependencies=[Depends(require_user)])
async def list_snapshots(limit: int = 20) -> Dict[str, object]:
    """List persisted snapshots for historical replay."""

    if limit < 1:
        raise HTTPException(400, "limit must be positive")
    limit = min(limit, 500)
    with SessionLocal() as db:
        rows: List[LiveSnapshotRecord] = (
            db.query(LiveSnapshotRecord)
            .order_by(desc(LiveSnapshotRecord.created_at))
            .limit(limit)
            .all()
        )
    return {
        "ok": True,
        "snapshots": [
            {
                "id": row.id,
                "reason": row.reason,
                "capturedAt": format_iso_datetime(row.created_at),
                "fixtureCount": len((row.payload or {}).get("fixtures") or []),
                "eventCount": _event_count(row.payload or {}),
            }
            for row in rows
        ],
    }


@router.get("/snapshots/{snapshot_id}", dependencies=[Depends(require_user)])
async def get_snapshot(snapshot_id: int) -> Dict[str, object]:
    """Return a snapshot payload with associated predictions and value bets."""

    with SessionLocal() as db:
        snap = db.get(LiveSnapshotRecord, snapshot_id)
        if not snap:
            raise HTTPException(404, f"Snapshot {snapshot_id} not found")
        prediction = (
            db.query(PredictionSnapshotRecord)
            .filter(PredictionSnapshotRecord.snapshot_id == snapshot_id)
            .order_by(desc(PredictionSnapshotRecord.created_at))
            .first()
        )
        value_bets = (
            db.query(ValueBetSnapshotRecord)
            .filter(ValueBetSnapshotRecord.snapshot_id == snapshot_id)
            .order_by(desc(ValueBetSnapshotRecord.created_at))
            .first()
        )

    return {
        "ok": True,
        "snapshot": {
            "id": snap.id,
            "capturedAt": format_iso_datetime(snap.created_at),
            "reason": snap.reason,
            "payload": snap.payload,
        },
        "predictions": prediction.payload if prediction else [],
        "valueBets": value_bets.payload if value_bets else [],
    }


@router.get("/fixtures/{fixture_id}/timeline", dependencies=[Depends(require_user)])
async def fixture_timeline(fixture_id: str, limit: int = 50) -> Dict[str, object]:
    """Replay a fixture's event feed across historical snapshots."""

    if limit < 1:
        raise HTTPException(400, "limit must be positive")
    limit = min(limit, 500)
    with SessionLocal() as db:
        snaps: List[LiveSnapshotRecord] = (
            db.query(LiveSnapshotRecord)
            .order_by(LiveSnapshotRecord.created_at.asc())
            .limit(limit)
            .all()
        )

    timeline: List[Dict[str, object]] = []
    for snap in snaps:
        payload = snap.payload or {}
        fixture_events = (payload.get("events") or {}).get(str(fixture_id)) or []
        event_feed = (payload.get("eventFeed") or {}).get(str(fixture_id)) or {}
        if fixture_events or event_feed:
            timeline.append(
                {
                    "capturedAt": format_iso_datetime(snap.created_at),
                    "events": fixture_events,
                    "eventFeed": event_feed,
                }
            )

    if not timeline:
        raise HTTPException(404, f"No events found for fixture {fixture_id}")

    return {"ok": True, "fixtureId": fixture_id, "timeline": timeline}
