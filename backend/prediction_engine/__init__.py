from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

from backend.db import SessionLocal
from backend.market.implied_probability import decimal_to_implied, normalize_probabilities
from backend.prediction_engine.engine import PredictionEngine, PredictionInput, TARGET_OVERROUND
from backend.prediction_engine.strength.team_strength import MatchResult
from backend.stats_context import build_poisson_context
from backend.validation import parse_iso_datetime, parse_market_line, require_decimal_odds
from backend.value.ev import expected_value
from backend.value.filters import apply_threshold

MODEL_VERSION = os.getenv("MODEL_VERSION", "ens_v2.1")
FORM_WINDOW = int(os.getenv("FORM_WINDOW", "5"))
BASE_HOME_GOALS = float(os.getenv("BASE_HOME_GOALS", "1.45"))
BASE_AWAY_GOALS = float(os.getenv("BASE_AWAY_GOALS", "1.15"))
DIXON_COLES_RHO = float(os.getenv("DIXON_COLES_RHO", "-0.08"))
EV_MIN_THRESHOLD = float(os.getenv("EV_MIN_THRESHOLD", "0.02"))


def _market_label(home: str | None, away: str | None) -> str:
    return f"{home or 'Home'} vs {away or 'Away'}"


def _fixture_timestamp(fixture: dict) -> Optional[datetime]:
    raw = fixture.get("startTime")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(parse_iso_datetime(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _collect_recent_results(snapshot: dict) -> List[Tuple[Optional[datetime], MatchResult]]:
    results: List[Tuple[Optional[datetime], MatchResult]] = []
    for fixture in snapshot.get("fixtures", []) or []:
        if fixture.get("status") != "finished":
            continue
        score = fixture.get("score") or {}
        if score.get("home") is None or score.get("away") is None:
            continue
        home_team = fixture.get("homeTeam")
        away_team = fixture.get("awayTeam")
        if not home_team or not away_team:
            continue
        result = MatchResult(
            home_team=home_team,
            away_team=away_team,
            home_goals=int(score["home"]),
            away_goals=int(score["away"]),
            league=fixture.get("league") or "Unknown",
        )
        results.append((_fixture_timestamp(fixture), result))
    return results


def _team_form(results: List[Tuple[Optional[datetime], MatchResult]], team: str) -> float:
    if not team:
        return 0.5
    ordered = sorted(
        [item for item in results if item[1].home_team == team or item[1].away_team == team],
        key=lambda item: item[0] or datetime.min,
    )
    if not ordered:
        return 0.5
    recent = ordered[-FORM_WINDOW:]
    points = 0
    for _, match in recent:
        if match.home_goals == match.away_goals:
            points += 1
        elif match.home_team == team and match.home_goals > match.away_goals:
            points += 3
        elif match.away_team == team and match.away_goals > match.home_goals:
            points += 3
    return points / (3 * len(recent))


def _clean_odds_map(odds: Dict[str, float]) -> Dict[str, float]:
    cleaned: Dict[str, float] = {}
    for key, value in odds.items():
        try:
            cleaned[key] = require_decimal_odds(float(value), key)
        except (TypeError, ValueError):
            continue
    return cleaned


def _build_odds_lookup(snapshot: dict) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    by_fixture: Dict[str, Dict[str, float]] = {}
    by_label: Dict[str, Dict[str, float]] = {}
    for row in snapshot.get("odds", []) or []:
        odds = _clean_odds_map(
            {
                "home": row.get("home"),
                "draw": row.get("draw"),
                "away": row.get("away"),
            }
        )
        if {"home", "draw", "away"} <= set(odds):
            fixture_id = row.get("fixtureId") or row.get("fixture_id")
            if fixture_id:
                by_fixture[str(fixture_id)] = odds
            label = row.get("market")
            if label:
                by_label[label] = odds
    return by_fixture, by_label


def _prediction_input_from_fixture(
    fixture: dict,
    odds: Dict[str, float],
    recent_results: List[Tuple[Optional[datetime], MatchResult]],
    db,
) -> Optional[PredictionInput]:
    home_team = fixture.get("homeTeam")
    away_team = fixture.get("awayTeam")
    if not home_team or not away_team:
        return None

    league = fixture.get("league") or "Unknown"
    league_id = fixture.get("leagueId") or fixture.get("league_id") or league
    ctx = build_poisson_context(db, str(league_id), home_team, away_team)

    base_home = ctx.get("avg_goals_home_league", BASE_HOME_GOALS)
    base_away = ctx.get("avg_goals_away_league", BASE_AWAY_GOALS)
    return PredictionInput(
        fixture_id=str(fixture.get("id")),
        league=league,
        home_team=home_team,
        away_team=away_team,
        odds=odds,
        recent_results=[match for _, match in recent_results],
        base_home_goals=float(base_home),
        base_away_goals=float(base_away),
        home_attack=float(ctx.get("home_attack", 1.0)),
        away_attack=float(ctx.get("away_attack", 1.0)),
        home_defence=float(ctx.get("home_defense", 1.0)),
        away_defence=float(ctx.get("away_defense", 1.0)),
        form_home=_team_form(recent_results, home_team),
        form_away=_team_form(recent_results, away_team),
        dixon_coles_rho=DIXON_COLES_RHO,
    )


def _normalize_probabilities(probs: Dict[str, float]) -> Dict[str, float]:
    return normalize_probabilities({k: max(float(v), 0.0) for k, v in probs.items()})


def generate_predictions(snapshot: dict) -> List[Dict]:
    odds_by_fixture, odds_by_label = _build_odds_lookup(snapshot)
    recent_results = _collect_recent_results(snapshot)
    engine = PredictionEngine()
    predictions: List[Dict] = []

    with SessionLocal() as db:
        for fixture in snapshot.get("fixtures", []) or []:
            fixture_id = fixture.get("id")
            if fixture_id is None:
                continue
            fixture_id = str(fixture_id)
            odds = odds_by_fixture.get(fixture_id) or odds_by_label.get(
                _market_label(fixture.get("homeTeam"), fixture.get("awayTeam"))
            )
            inp = _prediction_input_from_fixture(fixture, odds or {}, recent_results, db)
            if not inp:
                continue
            result = engine.predict(inp)
            probs = _normalize_probabilities(result["probabilities"])
            priced_raw = {k: float(v) for k, v in (result.get("priced_probabilities") or {}).items()}
            priced_sum = sum(priced_raw.values()) or TARGET_OVERROUND
            priced = {k: v * (TARGET_OVERROUND / priced_sum) for k, v in priced_raw.items()}
            final_odds = {k: float(v) for k, v in (result.get("final_odds") or {}).items()}
            predictions.append(
                {
                    "fixtureId": fixture_id,
                    "homeWinProbability": round(probs["home"], 4),
                    "drawProbability": round(probs["draw"], 4),
                    "awayWinProbability": round(probs["away"], 4),
                    "pricedProbabilities": {k: round(v, 4) for k, v in priced.items()},
                    "finalOdds": {k: round(v, 4) for k, v in final_odds.items()},
                    "modelVersion": result.get("model_version", MODEL_VERSION),
                    "confidence": round(float(result.get("confidence", 0.0)), 4),
                }
            )

    return predictions


def _extract_totals_probabilities(matrix: np.ndarray, line: float) -> Dict[str, float]:
    goals = np.add.outer(
        np.arange(matrix.shape[0], dtype=float),
        np.arange(matrix.shape[1], dtype=float),
    )
    over_prob = float(matrix[goals > line].sum())
    under_prob = float(matrix[goals <= line].sum())
    return _normalize_probabilities({"over": over_prob, "under": under_prob})


def _extract_btts_probabilities(matrix: np.ndarray) -> Dict[str, float]:
    home_zero = float(matrix[0, :].sum())
    away_zero = float(matrix[:, 0].sum())
    both_zero = float(matrix[0, 0])
    yes_prob = 1.0 - (home_zero + away_zero - both_zero)
    no_prob = 1.0 - yes_prob
    return _normalize_probabilities({"yes": yes_prob, "no": no_prob})


def _extract_handicap_probabilities(matrix: np.ndarray, line: float) -> Dict[str, float]:
    home_range = np.arange(matrix.shape[0], dtype=float).reshape(-1, 1)
    away_range = np.arange(matrix.shape[1], dtype=float).reshape(1, -1)
    diff = home_range - away_range
    push_mask = np.isclose(diff, line)
    home_cover = float(matrix[(diff > line) & (~push_mask)].sum())
    push = float(matrix[push_mask].sum())
    away_cover = float(matrix[(diff < line) & (~push_mask)].sum())
    return _normalize_probabilities({"home": home_cover, "away": away_cover, "push": push})


def _player_prop_probabilities(cleaned: Dict[str, float], ctx: dict) -> Dict[str, float]:
    """Lightweight player prop calculator using implied probabilities with team strength nudges."""

    implied = decimal_to_implied(cleaned)
    attack = float(ctx.get("home_attack") or ctx.get("attack") or 1.0)
    defense = float(ctx.get("away_defense") or ctx.get("away_defence") or ctx.get("defense") or 1.0)
    strength_adjustment = max(min((attack - defense) * 0.1, 0.15), -0.15)
    adjusted = {k: max(v * (1 + strength_adjustment), 0.0) for k, v in implied.items()}
    return _normalize_probabilities(adjusted)


def _map_outcome_1x2(outcome: str) -> Optional[str]:
    lower = outcome.lower()
    if lower in {"home", "1", "h"}:
        return "home"
    if lower in {"draw", "x", "d"}:
        return "draw"
    if lower in {"away", "2", "a"}:
        return "away"
    return None


def _map_outcome_over_under(outcome: str) -> Optional[str]:
    lower = outcome.lower()
    if lower.startswith("over"):
        return "over"
    if lower.startswith("under"):
        return "under"
    return None


def _map_outcome_btts(outcome: str) -> Optional[str]:
    lower = outcome.lower()
    if lower in {"gg", "yes", "both"} or "yes" in lower:
        return "yes"
    if lower in {"ng", "no"} or "no" in lower:
        return "no"
    return None


def _map_outcome_handicap(outcome: str) -> Optional[str]:
    lower = outcome.lower()
    if "home" in lower or lower.startswith("-") or lower.startswith("1"):
        return "home"
    if "away" in lower or lower.startswith("+") or lower.startswith("2"):
        return "away"
    return None


def _identity(outcome: str) -> str:
    return outcome


def predict_market(market: str, odds: Dict[str, float], ctx: dict) -> Dict[str, Dict[str, float]]:
    """Predict a market and compute EV for each listed outcome."""

    cleaned = _clean_odds_map(odds)
    if not cleaned:
        return {}

    market_lower = (market or "").lower()
    engine = PredictionEngine()
    inp = PredictionInput(
        fixture_id=str(ctx.get("fixture_id") or "alert"),
        league=str(ctx.get("league_id") or ctx.get("league") or "Unknown"),
        home_team=str(ctx.get("home_team") or ctx.get("home") or "Home"),
        away_team=str(ctx.get("away_team") or ctx.get("away") or "Away"),
        odds=cleaned,
        recent_results=[],
        base_home_goals=float(ctx.get("avg_goals_home_league", BASE_HOME_GOALS)),
        base_away_goals=float(ctx.get("avg_goals_away_league", BASE_AWAY_GOALS)),
        home_attack=float(ctx.get("home_attack", 1.0)),
        away_attack=float(ctx.get("away_attack", 1.0)),
        home_defence=float(ctx.get("home_defense", 1.0)),
        away_defence=float(ctx.get("away_defense", 1.0)),
        dixon_coles_rho=DIXON_COLES_RHO,
    )
    poisson = engine.poisson_prediction(inp)

    probabilities: Dict[str, float]
    if market_lower in {"1x2", "match winner", "match winner 1x2"}:
        probabilities = _normalize_probabilities(poisson.one_x_two)
        mapper = _map_outcome_1x2
    elif "over/under" in market_lower or "total" in market_lower:
        line = None
        for outcome in cleaned:
            mapped = _map_outcome_over_under(outcome)
            if mapped:
                parts = outcome.split()
                if len(parts) >= 2:
                    try:
                        line = parse_market_line(parts[1])
                    except ValueError:
                        continue
        if line is None:
            implied = normalize_probabilities(decimal_to_implied(cleaned))
            probabilities = implied
            mapper = _map_outcome_over_under
        else:
            probabilities = _extract_totals_probabilities(poisson.score_matrix, line)
            mapper = _map_outcome_over_under
    elif "asian" in market_lower or "handicap" in market_lower:
        line = None
        for outcome in cleaned:
            tokens = outcome.replace("+", " +").replace("-", " -").split()
            for token in tokens:
                try:
                    line = float(token)
                    break
                except ValueError:
                    continue
            if line is not None:
                break
        line = 0.0 if line is None else line
        probabilities = _extract_handicap_probabilities(poisson.score_matrix, line)
        mapper = _map_outcome_handicap
    elif "player" in market_lower or "goalscorer" in market_lower or "shots" in market_lower:
        probabilities = _player_prop_probabilities(cleaned, ctx)
        mapper = _identity
    elif "both teams" in market_lower or "btts" in market_lower:
        probabilities = _extract_btts_probabilities(poisson.score_matrix)
        mapper = _map_outcome_btts
    else:
        probabilities = normalize_probabilities(decimal_to_implied(cleaned))
        mapper = _identity

    response: Dict[str, Dict[str, float]] = {}
    for outcome, price in cleaned.items():
        key = mapper(outcome) if mapper else outcome
        if key is None or key not in probabilities:
            continue
        prob = float(probabilities[key])
        ev = expected_value(prob, price)
        response[outcome] = {"prob": round(prob, 4), "ev": round(ev, 4)}

    return response


def compute_value_bets(snapshot: dict, min_ev: float | None = None) -> List[Dict]:
    odds_by_fixture, odds_by_label = _build_odds_lookup(snapshot)
    fixtures = {
        str(fx.get("id")): fx
        for fx in snapshot.get("fixtures", []) or []
        if fx.get("id") is not None
    }
    predictions = generate_predictions(snapshot)
    threshold = EV_MIN_THRESHOLD if min_ev is None else min_ev
    value_bets: List[Dict] = []

    for pred in predictions:
        fixture_id = pred.get("fixtureId")
        fixture = fixtures.get(fixture_id)
        if not fixture:
            continue
        label = _market_label(fixture.get("homeTeam"), fixture.get("awayTeam"))
        odds = odds_by_fixture.get(fixture_id) or odds_by_label.get(label)
        if not odds:
            continue
        for outcome, prob_key in (
            ("home", "homeWinProbability"),
            ("draw", "drawProbability"),
            ("away", "awayWinProbability"),
        ):
            price = odds.get(outcome)
            if not price:
                continue
            prob = float(pred.get(prob_key) or 0)
            ev = expected_value(prob, price)
            value_bets.append(
                {
                    "match": label,
                    "market": f"Match Winner - {outcome.title()}",
                    "odds": price,
                    "modelProbability": round(prob, 4),
                    "expectedValue": round(ev, 4),
                }
            )

    filtered = apply_threshold({idx: row["expectedValue"] for idx, row in enumerate(value_bets)}, min_ev=threshold)
    kept = [row for idx, row in enumerate(value_bets) if idx in filtered]
    kept.sort(key=lambda row: row["expectedValue"], reverse=True)
    return kept
