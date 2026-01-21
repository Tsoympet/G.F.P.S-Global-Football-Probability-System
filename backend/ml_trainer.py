"""Training scheduler that persists model versions and metrics."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from sklearn.metrics import log_loss

from .db import SessionLocal
from .models import LiveSnapshotRecord, ModelVersion, TeamStats, TrainingRun
from .ml.build_features import build_feature_matrix, build_label_vector
from .ml.feature_schema import MatchFeatures
from .ml.multiclass_model import train_logistic
from .market.implied_probability import normalize_probabilities, decimal_to_implied
from .prediction_engine import FORM_WINDOW
from .validation import parse_iso_datetime, require_decimal_odds


def _fixture_timestamp(fixture: dict) -> Optional[datetime]:
    raw = fixture.get("startTime")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(parse_iso_datetime(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _outcome_from_score(score: dict) -> Optional[str]:
    if score.get("home") is None or score.get("away") is None:
        return None
    home_goals = score["home"]
    away_goals = score["away"]
    if home_goals > away_goals:
        return "home"
    if away_goals > home_goals:
        return "away"
    return "draw"


def _team_form(results: Iterable[Tuple[datetime, dict]], team: str, cutoff: datetime) -> float:
    matches = [
        (ts, fx)
        for ts, fx in results
        if ts < cutoff and (fx.get("homeTeam") == team or fx.get("awayTeam") == team)
    ]
    if not matches:
        return 0.5
    matches.sort(key=lambda item: item[0])
    recent = matches[-FORM_WINDOW:]
    points = 0
    for _, fixture in recent:
        score = fixture.get("score") or {}
        outcome = _outcome_from_score(score)
        if outcome is None:
            continue
        if outcome == "draw":
            points += 1
        elif outcome == "home" and fixture.get("homeTeam") == team:
            points += 3
        elif outcome == "away" and fixture.get("awayTeam") == team:
            points += 3
    return points / (3 * len(recent))


def _build_training_rows(
    snapshots: Iterable[LiveSnapshotRecord],
) -> Tuple[List[MatchFeatures], List[str], List[Dict[str, float]]]:
    fixtures: List[Tuple[datetime, dict]] = []
    odds_lookup: Dict[str, Dict[str, float]] = {}

    for snap in snapshots:
        payload = snap.payload or {}
        for row in payload.get("odds", []) or []:
            fixture_id = row.get("fixtureId") or row.get("fixture_id")
            if not fixture_id:
                continue
            try:
                odds_lookup[str(fixture_id)] = {
                    "home": require_decimal_odds(float(row.get("home") or 0), "home"),
                    "draw": require_decimal_odds(float(row.get("draw") or 0), "draw"),
                    "away": require_decimal_odds(float(row.get("away") or 0), "away"),
                }
            except ValueError:
                continue
        for fixture in payload.get("fixtures", []) or []:
            timestamp = _fixture_timestamp(fixture)
            if not timestamp:
                continue
            fixtures.append((timestamp, fixture))

    fixtures.sort(key=lambda item: item[0])
    features: List[MatchFeatures] = []
    labels: List[str] = []
    odds_rows: List[Dict[str, float]] = []

    last_played: Dict[str, datetime] = {}
    with SessionLocal() as db:
        for ts, fixture in fixtures:
            if fixture.get("status") != "finished":
                continue
            score = fixture.get("score") or {}
            outcome = _outcome_from_score(score)
            if outcome is None:
                continue
            fixture_id = str(fixture.get("id"))
            odds = odds_lookup.get(fixture_id)
            if not odds:
                continue

            home_team = fixture.get("homeTeam")
            away_team = fixture.get("awayTeam")
            league_id = fixture.get("leagueId") or fixture.get("league_id") or "unknown"
            if not home_team or not away_team:
                continue

            home_stats = (
                db.query(TeamStats)
                .filter(TeamStats.league_id == str(league_id), TeamStats.team_name == home_team)
                .first()
            )
            away_stats = (
                db.query(TeamStats)
                .filter(TeamStats.league_id == str(league_id), TeamStats.team_name == away_team)
                .first()
            )
            home_strength = (
                home_stats.home_attack / max(home_stats.home_defense, 0.1) if home_stats else 1.0
            )
            away_strength = (
                away_stats.away_attack / max(away_stats.away_defense, 0.1) if away_stats else 1.0
            )

            home_form = _team_form(fixtures, home_team, ts)
            away_form = _team_form(fixtures, away_team, ts)

            rest_home = (ts - last_played.get(home_team, ts)).total_seconds() / 86400.0
            rest_away = (ts - last_played.get(away_team, ts)).total_seconds() / 86400.0
            rest_diff = rest_home - rest_away
            last_played[home_team] = ts
            last_played[away_team] = ts

            implied = normalize_probabilities(decimal_to_implied(odds))
            features.append(
                MatchFeatures(
                    fixture_id=fixture_id,
                    league=fixture.get("league") or "Unknown",
                    home_team=home_team,
                    away_team=away_team,
                    home_strength=float(home_strength),
                    away_strength=float(away_strength),
                    form_diff=float(home_form - away_form),
                    rest_diff=float(rest_diff),
                    implied_home=float(implied.get("home", 0.0)),
                    implied_draw=float(implied.get("draw", 0.0)),
                    implied_away=float(implied.get("away", 0.0)),
                    player_rating_diff=float(fixture.get("playerRatingDiff") or 0.0),
                    injury_diff=float(fixture.get("injuryDiff") or 0.0),
                    weather_temp_c=float(fixture.get("weather", {}).get("tempC") if fixture.get("weather") else 0.0),
                    weather_wind_mps=float(fixture.get("weather", {}).get("windMps") if fixture.get("weather") else 0.0),
                    venue_altitude_m=float(fixture.get("venue", {}).get("altitudeM") if fixture.get("venue") else 0.0),
                    live_xg_diff=float(fixture.get("liveXgDiff") or 0.0),
                )
            )
            labels.append(outcome)
            odds_rows.append(odds)

    return features, labels, odds_rows


def _roi_from_predictions(
    probs: np.ndarray, labels: List[str], odds_rows: List[Dict[str, float]]
) -> float:
    mapping = {0: "home", 1: "draw", 2: "away"}
    pnl = 0.0
    stake = 0.0
    for row_probs, label, odds in zip(probs, labels, odds_rows):
        pick = mapping[int(np.argmax(row_probs))]
        price = odds.get(pick)
        if not price:
            continue
        stake += 1.0
        pnl += price - 1.0 if pick == label else -1.0
    return pnl / stake if stake else 0.0


def _train_model(run_id: int, version: str) -> None:
    with SessionLocal() as db:
        snapshots = db.query(LiveSnapshotRecord).order_by(LiveSnapshotRecord.created_at.desc()).all()

    features, labels, odds_rows = _build_training_rows(snapshots)
    if not features:
        with SessionLocal() as db:
            run = db.get(TrainingRun, run_id)
            if run:
                run.status = "failed"
                run.metrics = {"error": "No completed fixtures with odds available"}
                run.completed_at = datetime.now(timezone.utc)
                db.add(run)
                db.commit()
        return
    if len(set(labels)) < 2:
        with SessionLocal() as db:
            run = db.get(TrainingRun, run_id)
            if run:
                run.status = "failed"
                run.metrics = {"error": "Insufficient outcome diversity for training"}
                run.completed_at = datetime.now(timezone.utc)
                db.add(run)
                db.commit()
        return

    matrix, _ = build_feature_matrix(features)
    X = matrix.to_numpy(dtype=float)
    y = build_label_vector(labels)
    bundle = train_logistic(X, y)
    probs = bundle.predict_proba(X)
    metrics = {
        "logLoss": float(log_loss(y, probs)),
        "roi": float(_roi_from_predictions(probs, labels, odds_rows)),
        "samples": int(len(labels)),
    }

    with SessionLocal() as db:
        run = db.get(TrainingRun, run_id)
        if run:
            run.status = "completed"
            run.metrics = metrics
            run.completed_at = datetime.now(timezone.utc)
            db.add(run)

        model = db.query(ModelVersion).filter(ModelVersion.version == version).first()
        if not model:
            model = ModelVersion(version=version, status="ready", metrics=metrics)
        else:
            model.metrics = metrics
            model.status = "ready"
        db.add(model)
        db.commit()


async def _run_training(run_id: int, version: str) -> None:
    """Execute training work in a thread; _train_model handles success/failure persistence and model updates."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _train_model, run_id, version)


def queue_training(loop: asyncio.AbstractEventLoop, version: str) -> int:
    with SessionLocal() as db:
        run = TrainingRun(version=version, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

    loop.create_task(_run_training(run.id, version))
    return run.id
