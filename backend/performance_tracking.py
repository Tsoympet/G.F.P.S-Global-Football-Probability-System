from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from statistics import mean, pvariance
from typing import Dict, Iterable, List, Optional, Tuple

from .db import SessionLocal
from .models import (
    BacktestRun,
    BetJournalEntry,
    LiveSnapshotRecord,
    PredictionSnapshotRecord,
    ResultEntity,
)

EPSILON = 1e-9
MIN_SAMPLE_SIZE_WARNING = 30


@dataclass
class JournalRow:
    stake: float
    ev: float
    result: Optional[str]
    realized_roi: Optional[float]
    market: str
    league: str
    home_team: str
    away_team: str
    created_at: datetime
    side: str
    bookmaker_odds: Optional[float] = None
    closing_odds: Optional[float] = None
    fair_odds: Optional[float] = None


@dataclass
class BacktestRules:
    markets: List[str]
    min_ev: float = 0.0
    min_confidence: float = 0.0
    max_per_day: int = 5
    league_whitelist: Optional[List[str]] = None
    league_blacklist: Optional[List[str]] = None
    team_whitelist: Optional[List[str]] = None
    exclude_correlated_above: Optional[float] = 0.5
    stake_model: str = "flat"  # flat | kelly
    base_stake: float = 1.0
    kelly_fraction: float = 0.25
    stake_cap: Optional[float] = None
    use_fair_odds_if_missing: bool = True


@dataclass
class BacktestSnapshot:
    timestamp: datetime
    fixtures: List[dict]
    predictions: List[dict]
    odds_by_fixture: Dict[str, Dict[str, float]]


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _pnl(entry: JournalRow | BetJournalEntry) -> float:
    roi = entry.realized_roi or 0.0
    return roi * entry.stake


def _resolve_side(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if away_goals > home_goals:
        return "away"
    return "draw"


def _drawdown(values: Iterable[float]) -> Tuple[float, float, List[Dict[str, float]]]:
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    curve: List[Dict[str, float]] = []
    for idx, change in enumerate(values):
        equity += change
        peak = max(peak, equity)
        drawdown = peak - equity
        max_dd = max(max_dd, drawdown)
        curve.append({"idx": idx, "equity": equity, "drawdown": drawdown})
    current_dd = curve[-1]["drawdown"] if curve else 0.0
    return max_dd, current_dd, curve


def _group(entries: List[JournalRow], key_fn) -> List[Dict]:
    buckets: Dict[str, Dict[str, float]] = {}
    for row in entries:
        key = key_fn(row) or "Unknown"
        bucket = buckets.setdefault(key, {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0})
        bucket["count"] += 1
        bucket["profit"] += _pnl(row)
        bucket["stake"] += row.stake
        if row.result == "win":
            bucket["wins"] += 1
    response = []
    for key, bucket in buckets.items():
        stake = bucket["stake"]
        profit = bucket["profit"]
        roi = profit / stake if stake else 0.0
        hit_rate = bucket["wins"] / bucket["count"] if bucket["count"] else 0.0
        response.append({"label": key, "roi": roi, "hitRate": hit_rate, "count": bucket["count"]})
    response.sort(key=lambda r: r["roi"], reverse=True)
    return response


def settle_entry(entry: BetJournalEntry, actual_side: Optional[str], closing_odds: Optional[float] = None) -> BetJournalEntry:
    if entry.status == "settled":
        return entry

    odds = closing_odds or entry.bookmaker_odds or entry.fair_odds or 0.0
    entry.status = "settled"
    entry.settled_at = datetime.now(timezone.utc)
    if closing_odds:
        entry.closing_odds = closing_odds

    if not actual_side or not odds:
        entry.result = "void"
        entry.realized_roi = 0.0
        return entry

    if actual_side == entry.side:
        entry.result = "win"
        entry.realized_roi = odds - 1.0
    else:
        entry.result = "loss"
        entry.realized_roi = -1.0
    return entry


def reconcile_journal_entries() -> Dict[str, int]:
    """Settle any pending journal entries using stored results."""
    with SessionLocal() as db:
        pending = db.query(BetJournalEntry).filter(BetJournalEntry.status == "pending").all()
        if not pending:
            return {"settled": 0, "pending": 0}

        results = {res.fixture_id: res for res in db.query(ResultEntity).all()}
        settled = 0
        for entry in pending:
            resolved_side: Optional[str] = None
            for fid in entry.fixture_ids or []:
                res = results.get(str(fid))
                if res:
                    resolved_side = _resolve_side(res.home_score, res.away_score)
                    break
            if resolved_side:
                settle_entry(entry, resolved_side)
                db.add(entry)
                settled += 1
        if settled:
            db.commit()
        return {"settled": settled, "pending": len(pending) - settled}


def _window_filter(entries: List[JournalRow], days: int) -> List[JournalRow]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [row for row in entries if row.created_at and row.created_at >= cutoff]


def compute_performance_kpis(rows: Iterable[BetJournalEntry | JournalRow]) -> Dict:
    journal_rows: List[JournalRow] = []
    for row in rows:
        journal_rows.append(
            JournalRow(
                stake=row.stake,
                ev=row.ev,
                result=row.result,
                realized_roi=row.realized_roi,
                market=row.market,
                league=row.league,
                home_team=row.home_team,
                away_team=row.away_team,
                created_at=row.created_at or datetime.now(timezone.utc),
                side=row.side,
                bookmaker_odds=getattr(row, "bookmaker_odds", None),
                closing_odds=getattr(row, "closing_odds", None),
                fair_odds=getattr(row, "fair_odds", None),
            )
        )

    settled = [row for row in journal_rows if row.result]
    total = len(journal_rows)
    wins = len([r for r in settled if r.result == "win"])
    losses = len([r for r in settled if r.result == "loss"])
    pushes = len([r for r in settled if r.result in ("push", "void")])
    pending = total - len(settled)

    total_stake = sum(r.stake for r in settled) or 0.0
    profit = sum(_pnl(r) for r in settled)
    roi = profit / total_stake if total_stake else 0.0
    yield_per_bet = profit / len(settled) if settled else 0.0
    hit_rate = wins / len(settled) if settled else 0.0
    avg_ev = mean([r.ev for r in journal_rows]) if journal_rows else 0.0
    avg_realized_roi = mean([r.realized_roi or 0.0 for r in settled]) if settled else 0.0
    clv_samples: List[float] = []
    for r in settled:
        reference = r.closing_odds or r.fair_odds
        book = r.bookmaker_odds
        if reference and book and book > 0:
            clv_samples.append((reference - book) / book)
    clv_proxy = mean(clv_samples) if clv_samples else 0.0
    variance_proxy = pvariance([_pnl(r) for r in settled]) if len(settled) > 1 else 0.0

    ordered = sorted(settled, key=lambda r: r.created_at)
    pnl_series = [_pnl(r) for r in ordered]
    max_dd, current_dd, dd_curve = _drawdown(pnl_series)
    equity = []
    cum_profit = 0.0
    cum_stake = 0.0
    for row in ordered:
        cum_profit += _pnl(row)
        cum_stake += row.stake
        roi_point = cum_profit / cum_stake if cum_stake else 0.0
        equity.append({"timestamp": row.created_at.isoformat(), "roi": roi_point})

    def _window_stats(days: int) -> Dict[str, float]:
        subset = _window_filter(settled, days)
        stake = sum(r.stake for r in subset) or 0.0
        pnl = sum(_pnl(r) for r in subset)
        return {
            "count": len(subset),
            "roi": pnl / stake if stake else 0.0,
            "hitRate": len([r for r in subset if r.result == "win"]) / len(subset) if subset else 0.0,
        }

    breakdown_market = _group(settled, lambda r: r.market)
    breakdown_league = _group(settled, lambda r: r.league)
    breakdown_team = _group(
        settled,
        lambda r: f"{r.home_team} vs {r.away_team}" if r.home_team or r.away_team else "Unknown",
    )

    data_quality = {"pending": pending, "missing_results": pending}

    return {
        "totalBets": total,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "pending": pending,
        "roi": roi,
        "yield": yield_per_bet,
        "hitRate": hit_rate,
        "avgEv": avg_ev,
        "avgRealizedRoi": avg_realized_roi,
        "clvProxy": clv_proxy,
        "varianceProxy": variance_proxy,
        "maxDrawdown": max_dd,
        "currentDrawdown": current_dd,
        "drawdownCurve": dd_curve,
        "roiCurve": equity,
        "byMarket": breakdown_market,
        "byLeague": breakdown_league,
        "byTeam": breakdown_team,
        "windows": {
            "7d": _window_stats(7),
            "30d": _window_stats(30),
            "90d": _window_stats(90),
        },
        "dataQuality": data_quality,
    }


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except Exception:
        return None


def build_backtest_dataset(
    db,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Tuple[List[BacktestSnapshot], Dict[str, Dict[str, object]]]:
    query = db.query(LiveSnapshotRecord)
    if start:
        query = query.filter(LiveSnapshotRecord.created_at >= start)
    if end:
        query = query.filter(LiveSnapshotRecord.created_at <= end)

    snapshots: List[BacktestSnapshot] = []
    results: Dict[str, Dict[str, object]] = {}

    for snap in query.order_by(LiveSnapshotRecord.created_at.asc()).all():
        payload = snap.payload or {}
        fixtures = payload.get("fixtures") or []
        odds_by_fixture: Dict[str, Dict[str, float]] = {}
        for row in payload.get("odds") or []:
            fixture_id = str(row.get("fixtureId") or row.get("fixture_id") or row.get("fixture") or "")
            if not fixture_id:
                continue
            odds_by_fixture[fixture_id] = {
                "home": _as_float(row.get("home"), 0.0),
                "draw": _as_float(row.get("draw"), 0.0),
                "away": _as_float(row.get("away"), 0.0),
            }
        pred = (
            db.query(PredictionSnapshotRecord)
            .filter(PredictionSnapshotRecord.snapshot_id == snap.id)
            .order_by(PredictionSnapshotRecord.created_at.desc())
            .first()
        )
        predictions = pred.payload if pred else []
        snapshots.append(
            BacktestSnapshot(
                timestamp=snap.created_at or datetime.now(timezone.utc),
                fixtures=fixtures,
                predictions=predictions,
                odds_by_fixture=odds_by_fixture,
            )
        )

        for fx in fixtures:
            fid = str(fx.get("id") or "")
            if not fid or fid in results:
                continue
            score = fx.get("score") or {}
            if score.get("home") is None or score.get("away") is None:
                continue
            results[fid] = {
                "outcome": _resolve_side(int(score["home"]), int(score["away"])),
                "timestamp": _parse_datetime(fx.get("startTime")) or snap.created_at or datetime.now(timezone.utc),
            }

    for res in db.query(ResultEntity).all():
        results[str(res.fixture_id)] = {
            "outcome": _resolve_side(res.home_score, res.away_score),
            "timestamp": res.created_at or datetime.now(timezone.utc),
        }

    return snapshots, results


def _stake_for_pick(prob: float, odds: float, rules: BacktestRules) -> float:
    if rules.stake_model == "kelly":
        if odds <= 1.0:
            return 0.0
        edge = max(prob * odds - 1.0, 0.0)
        denominator = odds - 1.0 if odds - 1.0 != 0 else EPSILON
        fraction = edge / denominator
        stake = rules.base_stake * rules.kelly_fraction * fraction
    else:
        stake = rules.base_stake
    if rules.stake_cap is not None:
        stake = min(stake, rules.stake_cap)
    return max(stake, 0.0)


def run_backtest(
    snapshots: List[BacktestSnapshot],
    results: Dict[str, Dict[str, object]],
    rules: BacktestRules,
    seed: int = 0,
    enforce_anti_lookahead: bool = True,
) -> Dict:
    rng = random.Random(seed)

    def simulate(active_rules: BacktestRules) -> Tuple[Dict, List[float]]:
        trades: List[Dict] = []
        pnl_series: List[float] = []
        equity = 0.0
        missing_results = 0

        for snap in sorted(snapshots, key=lambda s: s.timestamp):
            fixture_index = {str(fx.get("id")): fx for fx in snap.fixtures if fx.get("id") is not None}
            candidates: List[Dict] = []
            for pred in snap.predictions or []:
                fixture_id = str(pred.get("fixtureId") or pred.get("fixture_id") or "")
                if not fixture_id:
                    continue
                fixture = fixture_index.get(fixture_id, {})
                if active_rules.markets and "1x2" not in active_rules.markets:
                    continue
                league = fixture.get("league") or "Unknown"
                if active_rules.league_whitelist and league not in active_rules.league_whitelist:
                    continue
                if active_rules.league_blacklist and league in active_rules.league_blacklist:
                    continue
                teams = {fixture.get("homeTeam"), fixture.get("awayTeam")}
                if active_rules.team_whitelist and not any(team in teams for team in active_rules.team_whitelist):
                    continue

                result_meta = results.get(fixture_id)
                if enforce_anti_lookahead and isinstance(result_meta.get("timestamp") if result_meta else None, datetime):
                    ts = result_meta["timestamp"]  # type: ignore[index]
                    if snap.timestamp and snap.timestamp >= ts:
                        continue

                odds = dict(snap.odds_by_fixture.get(fixture_id) or {})
                if pred.get("finalOdds"):
                    for key, val in (pred.get("finalOdds") or {}).items():
                        converted = _as_float(val, 0.0)
                        if converted > 0:
                            odds[key] = converted

                for side, prob_key in (
                    ("home", "homeWinProbability"),
                    ("draw", "drawProbability"),
                    ("away", "awayWinProbability"),
                ):
                    prob = _as_float(pred.get(prob_key), 0.0)
                    price = odds.get(side)
                    if not price and active_rules.use_fair_odds_if_missing and prob > 0:
                        price = 1.0 / prob
                    if not price:
                        continue
                    ev = prob * price - 1.0
                    if ev < active_rules.min_ev or prob <= 0:
                        continue
                    confidence = _as_float(pred.get("confidence"), 0.0)
                    if confidence < active_rules.min_confidence:
                        continue
                    correlation_risk = 1.0 if any(c["fixture_id"] == fixture_id for c in candidates) else 0.0
                    if (
                        active_rules.exclude_correlated_above is not None
                        and correlation_risk > active_rules.exclude_correlated_above
                    ):
                        continue
                    candidates.append(
                        {
                            "fixture_id": fixture_id,
                            "league": league,
                            "side": side,
                            "prob": prob,
                            "odds": price,
                            "ev": ev,
                            "confidence": confidence,
                            "timestamp": snap.timestamp,
                            "correlation_risk": correlation_risk,
                        }
                    )

            candidates.sort(key=lambda c: (-c["ev"], c["fixture_id"]))
            daily_counts: Dict[str, int] = {}
            for cand in candidates:
                date_key = (cand["timestamp"] or datetime.now(timezone.utc)).date().isoformat()
                count = daily_counts.get(date_key, 0)
                if active_rules.max_per_day and count >= active_rules.max_per_day:
                    continue
                daily_counts[date_key] = count + 1

                outcome_meta = results.get(cand["fixture_id"])
                realized_roi: Optional[float]
                status: str
                if outcome_meta and outcome_meta.get("outcome"):
                    realized_roi = cand["odds"] - 1.0 if outcome_meta["outcome"] == cand["side"] else -1.0
                    status = "settled"
                else:
                    realized_roi = 0.0
                    status = "open"
                    missing_results += 1

                stake = _stake_for_pick(cand["prob"], cand["odds"], active_rules)
                pnl = stake * realized_roi
                equity += pnl
                pnl_series.append(pnl)
                trades.append(
                    {
                        **cand,
                        "stake": stake,
                        "realized_roi": realized_roi,
                        "pnl": pnl,
                        "status": status,
                    }
                )

        total_stake = sum(t["stake"] for t in trades) or 0.0
        total_profit = sum(t["pnl"] for t in trades)
        max_dd, current_dd, dd_curve = _drawdown(pnl_series)
        settled_trades = [t for t in trades if t["status"] == "settled"]
        hit_rate = (
            len([t for t in settled_trades if t["realized_roi"] > 0]) / len(settled_trades)
            if settled_trades
            else 0.0
        )
        roi = total_profit / total_stake if total_stake else 0.0

        metrics = {
            "roi": roi,
            "yield": total_profit / len(trades) if trades else 0.0,
            "hitRate": hit_rate,
            "maxDrawdown": max_dd,
            "currentDrawdown": current_dd,
            "totalStake": total_stake,
            "profit": total_profit,
            "sampleSize": len(trades),
            "drawdownCurve": dd_curve,
            "returns": pnl_series,
            "missingResults": missing_results,
        }
        return metrics, pnl_series

    primary_metrics, pnl_series = simulate(rules)
    unclipped_rules = replace(rules, exclude_correlated_above=None)
    no_corr_metrics, _ = simulate(unclipped_rules)
    sample_size = primary_metrics["sampleSize"]
    missing = primary_metrics["missingResults"]

    sensitivity = []
    for delta in (0.0, 0.02, 0.05):
        variant_rules = replace(rules, min_ev=rules.min_ev + delta)
        metrics, _ = simulate(variant_rules)
        sensitivity.append({"evThreshold": variant_rules.min_ev, "roi": metrics["roi"]})

    warnings: List[str] = []
    if primary_metrics["sampleSize"] < MIN_SAMPLE_SIZE_WARNING:
        warnings.append("Sample size is small; treat ROI with caution.")
    if primary_metrics["missingResults"]:
        warnings.append("Some fixtures are missing results; ROI may be understated.")
    data_completeness = 0.0 if sample_size == 0 else max(0.0, 1 - missing / sample_size)

    primary_metrics.update(
        {
            "correlationImpact": {
                "withFilter": primary_metrics["roi"],
                "withoutFilter": no_corr_metrics["roi"],
            },
            "honesty": {
                "warnings": warnings,
                "dataCompleteness": data_completeness,
            },
            "sensitivity": sensitivity,
        }
    )

    return primary_metrics


def persist_backtest_run(user_id: Optional[int], params: dict, metrics: dict, seed: int, warnings: List[str]) -> BacktestRun:
    with SessionLocal() as db:
        run = BacktestRun(
            user_id=user_id,
            params=params,
            metrics=metrics,
            warnings=warnings,
            status="completed",
            seed=seed,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run
