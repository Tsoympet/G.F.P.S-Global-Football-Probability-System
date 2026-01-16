from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth_dependency import get_db, require_user
from .performance_tracking import (
    BacktestRules,
    compute_performance_kpis,
    build_backtest_dataset,
    persist_backtest_run,
    reconcile_journal_entries,
    run_backtest,
    settle_entry,
)
from .models import BacktestRun, BetJournalEntry, User

router = APIRouter(prefix="/performance", tags=["performance"])


class BetJournalCreate(BaseModel):
    fixture_id: str = Field(..., description="Fixture identifier")
    league: Optional[str] = ""
    league_id: Optional[str] = ""
    home_team: Optional[str] = ""
    away_team: Optional[str] = ""
    market: str = "1x2"
    line: Optional[float] = None
    side: str = Field(..., description="home/draw/away or selection key")
    model_probability: float = Field(..., ge=0, le=1)
    fair_odds: Optional[float] = None
    bookmaker_odds: Optional[float] = None
    ev: Optional[float] = None
    correlation_risk: Optional[float] = 0.0
    confidence: Optional[float] = 0.0
    stake: float = 1.0
    stake_rule: Optional[str] = None
    result: Optional[str] = Field(None, description="win/loss/push/void")
    closing_odds: Optional[float] = None


class BacktestRulePayload(BaseModel):
    markets: List[str] = Field(default_factory=lambda: ["1x2"])
    min_ev: float = 0.0
    min_confidence: float = 0.0
    max_per_day: int = 5
    league_whitelist: Optional[List[str]] = None
    league_blacklist: Optional[List[str]] = None
    team_whitelist: Optional[List[str]] = None
    correlation_threshold: Optional[float] = 0.5
    stake_model: str = "flat"
    base_stake: float = 1.0
    kelly_fraction: float = 0.25
    stake_cap: Optional[float] = None
    use_fair_odds_if_missing: bool = True


class BacktestRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rules: BacktestRulePayload = Field(default_factory=BacktestRulePayload)
    seed: int = 7


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _serialize_run(run: BacktestRun) -> dict:
    return {
        "id": run.id,
        "status": run.status,
        "params": run.params,
        "metrics": run.metrics,
        "warnings": run.warnings,
        "seed": run.seed,
        "startedAt": run.started_at.isoformat() if run.started_at else None,
        "completedAt": run.completed_at.isoformat() if run.completed_at else None,
    }


@router.get("/journal", dependencies=[Depends(require_user)])
async def list_journal(limit: int = 200, db: Session = Depends(get_db), user: User = Depends(require_user)):
    rows = (
        db.query(BetJournalEntry)
        .filter(BetJournalEntry.user_id == user.id)
        .order_by(BetJournalEntry.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "created_at": row.created_at,
            "fixture_ids": row.fixture_ids,
            "league": row.league,
            "league_id": row.league_id,
            "home_team": row.home_team,
            "away_team": row.away_team,
            "market": row.market,
            "line": row.line,
            "side": row.side,
            "model_probability": row.model_probability,
            "fair_odds": row.fair_odds,
            "bookmaker_odds": row.bookmaker_odds,
            "ev": row.ev,
            "correlation_risk": row.correlation_risk,
            "confidence": row.confidence,
            "stake": row.stake,
            "stake_rule": row.stake_rule,
            "status": row.status,
            "result": row.result,
            "realized_roi": row.realized_roi,
            "closing_odds": row.closing_odds,
        }
        for row in rows
    ]


@router.post("/journal", status_code=201)
async def record_journal_entry(
    payload: BetJournalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    ev = payload.ev
    if ev is None and payload.bookmaker_odds and payload.bookmaker_odds > 0:
        ev = payload.model_probability * payload.bookmaker_odds - 1.0
    if ev is None:
        ev = 0.0

    entry = BetJournalEntry(
        user_id=user.id,
        fixture_ids=[payload.fixture_id],
        league=payload.league or "",
        league_id=payload.league_id or "",
        home_team=payload.home_team or "",
        away_team=payload.away_team or "",
        market=payload.market,
        line=payload.line,
        side=payload.side,
        model_probability=payload.model_probability,
        fair_odds=payload.fair_odds,
        bookmaker_odds=payload.bookmaker_odds,
        closing_odds=payload.closing_odds,
        ev=ev or 0.0,
        correlation_risk=payload.correlation_risk or 0.0,
        confidence=payload.confidence or 0.0,
        stake=payload.stake,
        stake_rule=payload.stake_rule,
        status="pending",
    )
    if payload.result:
        entry.settled_at = datetime.now(timezone.utc)
        if payload.result == "win":
            settle_entry(entry, payload.side, payload.closing_odds)
        elif payload.result == "loss":
            entry.status = "settled"
            entry.result = "loss"
            entry.realized_roi = -1.0
            if payload.closing_odds:
                entry.closing_odds = payload.closing_odds
        elif payload.result in ("push", "void"):
            entry.status = "settled"
            entry.result = payload.result
            entry.realized_roi = 0.0
            if payload.closing_odds:
                entry.closing_odds = payload.closing_odds
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "status": entry.status, "ev": entry.ev}


@router.get("/kpis", dependencies=[Depends(require_user)])
async def performance_kpis(db: Session = Depends(get_db), user: User = Depends(require_user)):
    reconcile_journal_entries()
    rows = (
        db.query(BetJournalEntry)
        .filter(BetJournalEntry.user_id == user.id)
        .order_by(BetJournalEntry.created_at.asc())
        .all()
    )
    return compute_performance_kpis(rows)


@router.post("/reconcile", dependencies=[Depends(require_user)])
async def reconcile():
    return reconcile_journal_entries()


@router.post("/backtests", dependencies=[Depends(require_user)])
async def run_backtest_endpoint(
    request: BacktestRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    start = _parse_dt(request.start_date)
    end = _parse_dt(request.end_date)
    snapshots, result_map = build_backtest_dataset(db, start, end)
    rules = BacktestRules(
        markets=request.rules.markets,
        min_ev=request.rules.min_ev,
        min_confidence=request.rules.min_confidence,
        max_per_day=request.rules.max_per_day,
        league_whitelist=request.rules.league_whitelist,
        league_blacklist=request.rules.league_blacklist,
        team_whitelist=request.rules.team_whitelist,
        exclude_correlated_above=request.rules.correlation_threshold,
        stake_model=request.rules.stake_model,
        base_stake=request.rules.base_stake,
        kelly_fraction=request.rules.kelly_fraction,
        stake_cap=request.rules.stake_cap,
        use_fair_odds_if_missing=request.rules.use_fair_odds_if_missing,
    )
    metrics = run_backtest(snapshots, result_map, rules, seed=request.seed)
    warnings = metrics.get("honesty", {}).get("warnings", [])
    run = persist_backtest_run(user.id, request.model_dump(), metrics, seed=request.seed, warnings=warnings)
    return {"runId": run.id, "status": run.status, "metrics": metrics}


@router.get("/backtests", dependencies=[Depends(require_user)])
async def list_backtests(db: Session = Depends(get_db), user: User = Depends(require_user)):
    runs = (
        db.query(BacktestRun)
        .filter(BacktestRun.user_id == user.id)
        .order_by(BacktestRun.started_at.desc())
        .limit(20)
        .all()
    )
    return [_serialize_run(run) for run in runs]


@router.get("/backtests/{run_id}", dependencies=[Depends(require_user)])
async def get_backtest(run_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id, BacktestRun.user_id == user.id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _serialize_run(run)
