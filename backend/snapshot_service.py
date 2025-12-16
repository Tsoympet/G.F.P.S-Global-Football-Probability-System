"""Persistence helpers for live snapshots, predictions, and value bets."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional

from .db import SessionLocal
from .models import (
    LiveSnapshotRecord,
    PredictionSnapshotRecord,
    ValueBetSnapshotRecord,
)
from .prediction_engine import compute_value_bets, generate_predictions
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


async def capture_snapshot(reason: str = "manual", model_version: str = "demo") -> Dict:
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


def backfill_demo_if_empty() -> Optional[LiveSnapshotRecord]:
    with SessionLocal() as db:
        has_snapshot = db.query(LiveSnapshotRecord).first()
        if has_snapshot:
            return has_snapshot

    # Use the in-memory defaults to seed the persistence layer for offline use
    snapshot = live_state.snapshot()
    rec = _persist_live_snapshot(snapshot, reason="seed")
    _persist_predictions(rec.id, generate_predictions(snapshot), model_version="demo")
    _persist_value_bets(rec.id, compute_value_bets(snapshot), model_version="demo")
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
