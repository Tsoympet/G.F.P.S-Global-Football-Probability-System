"""
Odds snapshots capture & scheduling.

This module persists bookmaker odds over time with lightweight de-duplication and
provides helpers for closing line selection.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import logging

from .db import SessionLocal
from .models import OddsSnapshotRecord

DEDUP_WINDOW_SEC = int(os.getenv("ODDS_SNAPSHOT_DEDUP_SEC", "45"))
ODDS_COMPARISON_TOLERANCE = 1e-9

logger = logging.getLogger("gfps.odds_snapshots")


def _hash_payload(payload: Dict[str, Any]) -> str:
    try:
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    except Exception:
        return ""


def _normalize_line(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _selection_entries(row: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    fixture_id = str(
        row.get("fixtureId")
        or row.get("fixture_id")
        or row.get("fixture")
        or row.get("match_id")
        or ""
    )
    if not fixture_id:
        return []
    market_id = str(row.get("market") or row.get("market_id") or "1x2")
    line = _normalize_line(row.get("line"))
    is_live = bool(row.get("isLive") or row.get("live") or False)
    source_confidence = float(row.get("source_confidence") or row.get("confidence") or 1.0)
    payload_hash = _hash_payload(row)
    for selection_key in ("home", "draw", "away"):
        price = row.get(selection_key)
        try:
            odds_decimal = float(price)
        except (TypeError, ValueError):
            continue
        yield {
            "match_id": fixture_id,
            "market_id": market_id,
            "selection_id": selection_key,
            "line": line,
            "odds_decimal": odds_decimal,
            "is_live": is_live,
            "source_confidence": source_confidence,
            "raw_payload_hash": payload_hash,
        }


def _should_skip_duplicate(
    db,
    provider_id: str,
    entry: Dict[str, Any],
    captured_at: datetime,
) -> bool:
    recent = (
        db.query(OddsSnapshotRecord)
        .filter(
            OddsSnapshotRecord.provider_id == provider_id,
            OddsSnapshotRecord.match_id == entry["match_id"],
            OddsSnapshotRecord.market_id == entry["market_id"],
            OddsSnapshotRecord.selection_id == entry["selection_id"],
        )
        .order_by(OddsSnapshotRecord.captured_at.desc())
        .first()
    )
    if not recent or not recent.captured_at:
        return False
    recent_ts = recent.captured_at
    if recent_ts.tzinfo is None:
        recent_ts = recent_ts.replace(tzinfo=timezone.utc)
    if abs(recent.odds_decimal - entry["odds_decimal"]) > ODDS_COMPARISON_TOLERANCE:
        return False
    delta = abs((captured_at - recent_ts).total_seconds())
    return delta <= DEDUP_WINDOW_SEC


def record_odds_snapshots(
    odds_rows: Iterable[Dict[str, Any]],
    provider_id: str = "api-football",
    source_confidence: float = 1.0,
    is_live: bool = False,
    captured_at: Optional[datetime] = None,
) -> int:
    """
    Persist odds snapshots; returns number of rows inserted.
    """
    inserted = 0
    now = captured_at or datetime.now(timezone.utc)
    with SessionLocal() as db:
        for row in odds_rows or []:
            for entry in _selection_entries(row):
                entry.setdefault("source_confidence", source_confidence)
                entry.setdefault("is_live", is_live)
                if _should_skip_duplicate(db, provider_id, entry, now):
                    continue
                rec = OddsSnapshotRecord(
                    provider_id=provider_id,
                    match_id=entry["match_id"],
                    market_id=entry["market_id"],
                    selection_id=entry["selection_id"],
                    line=entry.get("line"),
                    odds_decimal=entry["odds_decimal"],
                    is_live=entry.get("is_live", False),
                    source_confidence=entry.get("source_confidence", 1.0),
                    raw_payload_hash=entry.get("raw_payload_hash"),
                    captured_at=now,
                )
                db.add(rec)
                inserted += 1
        if inserted:
            db.commit()
    return inserted


def closing_odds(match_id: str, market_id: str, selection_id: str, kickoff: datetime) -> Optional[float]:
    """
    Return the last odds snapshot at or before kickoff.
    """
    if not match_id:
        return None
    with SessionLocal() as db:
        rec = (
            db.query(OddsSnapshotRecord)
            .filter(
                OddsSnapshotRecord.match_id == str(match_id),
                OddsSnapshotRecord.market_id == str(market_id),
                OddsSnapshotRecord.selection_id == str(selection_id),
                OddsSnapshotRecord.captured_at <= kickoff,
            )
            .order_by(OddsSnapshotRecord.captured_at.desc())
            .first()
        )
        return rec.odds_decimal if rec else None


def provider_enabled() -> bool:
    """Return True if an odds provider is configured."""
    return bool(os.getenv("APIFOOTBALL_KEY") or os.getenv("ODDS_PROVIDER_ENABLED"))


def _compute_snapshot_interval(fixtures: List[Dict[str, Any]], now: datetime) -> int:
    """
    Adjust snapshot interval based on proximity to kickoff.
    """
    nearest = None
    for fx in fixtures or []:
        start_raw = fx.get("startTime") or fx.get("kickoff") or fx.get("date")
        try:
            dt = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        except Exception:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt < now:
            continue
        if nearest is None or dt < nearest:
            nearest = dt
    if nearest is None:
        return 1800  # 30m default
    ahead = (nearest - now).total_seconds()
    if ahead <= 300:
        return 120  # every 2 minutes near kickoff
    if ahead <= 1800:
        return 300  # every 5 minutes within 30 minutes
    return 1800


async def _pull_live_state_snapshot() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    from .live_state import live_state

    snap = live_state.snapshot()
    return snap.get("odds") or [], snap.get("fixtures") or []


async def odds_snapshot_scheduler(
    fetch_snapshot: Optional[callable] = None,
    provider_id: str = "api-football",
) -> None:
    """
    Periodically capture odds snapshots if a provider is configured.
    """
    if not provider_enabled():
        return

    fetch = fetch_snapshot or _pull_live_state_snapshot

    while True:
        try:
            odds_rows, fixtures = await fetch()
            if odds_rows:
                record_odds_snapshots(odds_rows, provider_id=provider_id)
            interval = _compute_snapshot_interval(fixtures, datetime.now(timezone.utc))
        except Exception as exc:  # pragma: no cover - observability only
            logger.exception("odds_snapshot_scheduler failed: %s", exc)
            interval = 600
        await asyncio.sleep(interval)


def start_odds_snapshot_scheduler(loop: asyncio.AbstractEventLoop, provider_id: str = "api-football") -> None:
    if not provider_enabled():
        return
    loop.create_task(odds_snapshot_scheduler(provider_id=provider_id))
