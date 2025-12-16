"""Core GFPS prediction engine orchestrating market, statistical, and ML models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional
import numpy as np

from backend.market.devig_shin import shin_probabilities
from backend.market.overround import fair_probs_from_overround
from backend.market.implied_probability import market_entropy, normalize_probabilities
from backend.prediction_engine.goals.poisson import PoissonParams, score_probabilities
from backend.prediction_engine.strength.team_strength import MatchResult, StrengthModel
from backend.prediction_engine.calibration.temperature_scaling import TemperatureScaler
from backend.prediction_engine.ensemble.linear_pooling import linear_pool
from backend.ml.feature_schema import MatchFeatures
from backend.ml.multiclass_model import ModelBundle


@dataclass(frozen=True)
class PredictionInput:
    fixture_id: str
    league: str
    home_team: str
    away_team: str
    odds: Dict[str, float]
    recent_results: Iterable[MatchResult]
    base_goal_rate: float = 1.35


class PredictionEngine:
    """End-to-end orchestrator for football probability estimation."""

    def __init__(self, ml_model: Optional[ModelBundle] = None) -> None:
        self.ml_model = ml_model

    def _market_view(self, odds: Dict[str, float]) -> Dict[str, float]:
        fair = fair_probs_from_overround(odds)
        shin = shin_probabilities(odds)
        pooled = {k: 0.5 * fair.get(k, 0.0) + 0.5 * shin.get(k, 0.0) for k in odds}
        return normalize_probabilities(pooled)

    def _poisson_view(self, inp: PredictionInput) -> Dict[str, float]:
        strength_model = StrengthModel()
        strength_model.fit(inp.recent_results)
        home_strength = strength_model.strength(inp.league, inp.home_team)
        away_strength = strength_model.strength(inp.league, inp.away_team)
        lambda_home = max(inp.base_goal_rate * home_strength.attack * away_strength.defence, 0.1)
        lambda_away = max(inp.base_goal_rate * away_strength.attack * home_strength.defence * 0.85, 0.1)
        params = PoissonParams(lambda_home=lambda_home, lambda_away=lambda_away)
        prediction = score_probabilities(params)
        return prediction.one_x_two

    def _ml_view(self, inp: PredictionInput, market_probs: Dict[str, float]) -> Optional[Dict[str, float]]:
        if self.ml_model is None:
            return None
        features = MatchFeatures(
            fixture_id=inp.fixture_id,
            league=inp.league,
            home_team=inp.home_team,
            away_team=inp.away_team,
            home_strength=1.0,
            away_strength=1.0,
            form_diff=0.0,
            rest_diff=0.0,
            implied_home=market_probs.get("home", 0.0),
            implied_draw=market_probs.get("draw", 0.0),
            implied_away=market_probs.get("away", 0.0),
        )
        vector = np.array([list(features.to_vector().values())])
        probs = self.ml_model.predict_proba(vector)[0]
        mapping = {0: "home", 1: "draw", 2: "away"}
        return {mapping[i]: float(probs[i]) for i in range(len(probs))}

    def _calibrate(self, probs: np.ndarray) -> np.ndarray:
        labels = np.argmax(probs, axis=1)
        scaler = TemperatureScaler.fit(probs, labels)
        return scaler.transform(probs)

    def predict(self, inp: PredictionInput) -> Dict[str, object]:
        market_probs = self._market_view(inp.odds)
        poisson_probs = self._poisson_view(inp)
        components = [np.array([poisson_probs["home"], poisson_probs["draw"], poisson_probs["away"]]),
                      np.array([market_probs["home"], market_probs["draw"], market_probs["away"]])]
        weights = [0.5, 0.5]
        if self.ml_model:
            ml_probs = self._ml_view(inp, market_probs)
            if ml_probs:
                components.append(np.array([ml_probs["home"], ml_probs["draw"], ml_probs["away"]]))
                weights.append(0.4)
                total_weight = sum(weights)
                weights = [w / total_weight for w in weights]
        pooled = linear_pool(components, weights)
        calibrated = self._calibrate(pooled.reshape(1, -1))[0]
        confidence = 1.0 - market_entropy({"home": calibrated[0], "draw": calibrated[1], "away": calibrated[2]}) / np.log(3)
        result = {
            "fixture_id": inp.fixture_id,
            "probabilities": {"home": calibrated[0], "draw": calibrated[1], "away": calibrated[2]},
            "model_version": "ens_v2.0",
            "confidence": confidence,
            "calibrated": True,
        }
        return result


