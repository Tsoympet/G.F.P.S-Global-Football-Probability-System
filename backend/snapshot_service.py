"""Persistence helpers for live snapshots, predictions, and value bets."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .db import SessionLocal
from .models import (
    LiveSnapshotRecord,
    PredictionSnapshotRecord,
    ValueBetSnapshotRecord,
)
from .prediction_engine import MODEL_VERSION, compute_value_bets, generate_predictions
from .live_state import live_state


SNAPSHOT_INTERVAL_SEC = int(os.getenv("SNAPSHOT_INTERVAL_SEC", "60"))

_lock = asyncio.Lock()


def _persist_live_snapshot(snapshot: Dict, reason: str) -> LiveSnapshotRecord:
    with SessionLocal() as db:
        rec = LiveSnapshotRecord(reason=reason, payload=snapshot)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec


def _persist_predictions(snapshot_id: int, rows: List[Dict], model_version: str) -> None:
    with SessionLocal() as db:
        rec = PredictionSnapshotRecord(
            snapshot_id=snapshot_id, payload=rows, model_version=model_version
        )
        db.add(rec)
        db.commit()


def _persist_value_bets(snapshot_id: int, rows: List[Dict], model_version: str) -> None:
    with SessionLocal() as db:
        rec = ValueBetSnapshotRecord(
            snapshot_id=snapshot_id, payload=rows, model_version=model_version
        )
        db.add(rec)
        db.commit()


async def capture_snapshot(reason: str = "manual", model_version: str = MODEL_VERSION) -> Dict:
    """Persist the in-memory state + derived analytics."""

    async with _lock:
        snapshot = live_state.snapshot()
        rec = await asyncio.get_running_loop().run_in_executor(
            None, _persist_live_snapshot, snapshot, reason
        )

        predictions = generate_predictions(snapshot)
        value_bets = compute_value_bets(snapshot)

        await asyncio.get_running_loop().run_in_executor(
            None, _persist_predictions, rec.id, predictions, model_version
        )
        await asyncio.get_running_loop().run_in_executor(
            None, _persist_value_bets, rec.id, value_bets, model_version
        )

    return snapshot


async def periodic_capture_loop():
    """Schedule continuous snapshotting so offline users can explore data."""

    while True:
        try:
            await capture_snapshot(reason="scheduled")
        except Exception as exc:  # pragma: no cover - observability only
            print(f"[snapshot] failed: {exc}")
        await asyncio.sleep(SNAPSHOT_INTERVAL_SEC)


def start_snapshot_scheduler(loop: asyncio.AbstractEventLoop) -> None:
    loop.create_task(periodic_capture_loop())


def backfill_seed_if_empty() -> Optional[LiveSnapshotRecord]:
    with SessionLocal() as db:
        has_snapshot = db.query(LiveSnapshotRecord).first()
        if has_snapshot:
            return has_snapshot

    # Use the in-memory defaults to seed the persistence layer for offline use
    snapshot = live_state.snapshot()
    rec = _persist_live_snapshot(snapshot, reason="seed")
    _persist_predictions(rec.id, generate_predictions(snapshot), model_version=MODEL_VERSION)
    _persist_value_bets(rec.id, compute_value_bets(snapshot), model_version=MODEL_VERSION)
    return rec


def latest_snapshot_payload() -> Optional[Dict]:
    with SessionLocal() as db:
        rec = (
            db.query(LiveSnapshotRecord)
            .order_by(LiveSnapshotRecord.created_at.desc())
            .first()
        )
        if not rec:
            return None
        return rec.payload


def _market_line_count(markets: Dict[str, List[Dict]]) -> int:
    return sum(len(lines) for lines in (markets or {}).values())


def _format_timestamp(value: Optional[datetime]) -> Optional[str]:
    if not value:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def latest_snapshot_summary() -> Optional[Dict]:
    with SessionLocal() as db:
        snapshot = (
            db.query(LiveSnapshotRecord)
            .order_by(LiveSnapshotRecord.created_at.desc())
            .first()
        )
        if not snapshot:
            return None
        prediction = (
            db.query(PredictionSnapshotRecord)
            .filter(PredictionSnapshotRecord.snapshot_id == snapshot.id)
            .order_by(PredictionSnapshotRecord.created_at.desc())
            .first()
        )
        value_bets = (
            db.query(ValueBetSnapshotRecord)
            .filter(ValueBetSnapshotRecord.snapshot_id == snapshot.id)
            .order_by(ValueBetSnapshotRecord.created_at.desc())
            .first()
        )

    payload = snapshot.payload or {}
    markets = payload.get("markets") or {}
    captured_at = _format_timestamp(snapshot.created_at)
    age_sec = None
    if snapshot.created_at:
        created_at = snapshot.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_sec = (datetime.now(timezone.utc) - created_at).total_seconds()

    return {
        "snapshotId": snapshot.id,
        "reason": snapshot.reason,
        "capturedAt": captured_at,
        "ageSec": age_sec,
        "fixtureCount": len(payload.get("fixtures") or []),
        "oddsCount": len(payload.get("odds") or []),
        "marketLineCount": _market_line_count(markets),
        "predictionCount": len(prediction.payload or []) if prediction else 0,
        "valueBetCount": len(value_bets.payload or []) if value_bets else 0,
        "modelVersion": prediction.model_version if prediction else MODEL_VERSION,
    }
