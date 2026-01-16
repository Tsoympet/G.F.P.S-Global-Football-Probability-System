"""Core GFPS prediction engine orchestrating market, statistical, and ML models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional
import os
import numpy as np

from backend.market.devig_shin import shin_probabilities
from backend.market.overround import fair_probs_from_overround
from backend.market.implied_probability import market_entropy, normalize_probabilities
from backend.market.bookmaker_consensus import BookmakerLine, weighted_by_sharpness
from backend.prediction_engine.goals.poisson import PoissonParams
from backend.prediction_engine.goals.dixon_coles import score_probabilities_dc
from backend.prediction_engine.strength.team_strength import MatchResult, StrengthModel
from backend.prediction_engine.calibration.temperature_scaling import TemperatureScaler, logits_from_probabilities
from backend.prediction_engine.calibration.boosting_head import BoostingCalibrationHead, load_boosting_head
from backend.prediction_engine.ensemble.linear_pooling import linear_pool
from backend.prediction_engine.ensemble.stacking import StackingEnsemble
from backend.ml.feature_schema import MatchFeatures
from backend.ml.multiclass_model import ModelBundle
from backend.odds_abstraction import resolve_odds_from_sources

MODEL_VERSION = os.getenv("MODEL_VERSION", "ens_v2.1")
FORM_WEIGHT = float(os.getenv("FORM_ADJUSTMENT_WEIGHT", "0.15"))
MIN_GOAL_RATE = float(os.getenv("MIN_GOAL_RATE", "0.05"))
MARKET_WEIGHT_MIN = float(os.getenv("MARKET_WEIGHT_MIN", "0.35"))
MARKET_WEIGHT_MAX = float(os.getenv("MARKET_WEIGHT_MAX", "0.7"))
TARGET_OVERROUND = float(os.getenv("TARGET_OVERROUND", "1.06"))
RISK_SHADING_STRENGTH = float(os.getenv("RISK_SHADING_STRENGTH", "0.15"))


@dataclass(frozen=True)
class PredictionInput:
    fixture_id: str
    league: str
    home_team: str
    away_team: str
    odds: Dict[str, float]
    recent_results: Iterable[MatchResult]
    base_home_goals: float = 1.45
    base_away_goals: float = 1.15
    home_attack: float = 1.0
    away_attack: float = 1.0
    home_defence: float = 1.0
    away_defence: float = 1.0
    form_home: float = 0.5
    form_away: float = 0.5
    dixon_coles_rho: float = -0.08
    bookmaker_lines: Optional[Iterable[BookmakerLine]] = None
    exposure: Optional[Dict[str, float]] = None


class PredictionEngine:
    """End-to-end orchestrator for football probability estimation."""

    def __init__(
        self,
        ml_model: Optional[ModelBundle] = None,
        calibrator: Optional[TemperatureScaler] = None,
        stacking_model: Optional[StackingEnsemble] = None,
        boosting_head: Optional[BoostingCalibrationHead] = None,
    ) -> None:
        self.ml_model = ml_model
        self.calibrator = calibrator or TemperatureScaler(temperature=1.0)
        self.stacking_model = stacking_model
        self.boosting_head = boosting_head or load_boosting_head()

    def market_probabilities(self, odds: Dict[str, float]) -> Dict[str, float]:
        if not odds:
            return {}
        fair = fair_probs_from_overround(odds)
        shin = shin_probabilities(odds)
        pooled = {k: 0.5 * fair.get(k, 0.0) + 0.5 * shin.get(k, 0.0) for k in odds}
        return normalize_probabilities(pooled)

    def consensus_probabilities(self, lines: Optional[Iterable[BookmakerLine]]) -> Dict[str, float]:
        if not lines:
            return {}
        consensus = weighted_by_sharpness(lines)
        return normalize_probabilities(consensus) if consensus else {}

    @staticmethod
    def _market_weight(probs: Dict[str, float]) -> float:
        confidence = 1.0 - market_entropy(probs) / np.log(3)
        return max(min(confidence, MARKET_WEIGHT_MAX), MARKET_WEIGHT_MIN)

    def poisson_prediction(self, inp: PredictionInput):
        strength_model = StrengthModel()
        strength_model.fit(inp.recent_results)
        home_strength = strength_model.strength(inp.league, inp.home_team)
        away_strength = strength_model.strength(inp.league, inp.away_team)
        home_attack = inp.home_attack * home_strength.attack
        away_attack = inp.away_attack * away_strength.attack
        home_defence = inp.home_defence * home_strength.defence
        away_defence = inp.away_defence * away_strength.defence

        form_diff = inp.form_home - inp.form_away
        form_adjustment = FORM_WEIGHT * form_diff
        lambda_home = inp.base_home_goals * home_attack * away_defence * (1 + form_adjustment)
        lambda_away = inp.base_away_goals * away_attack * home_defence * (1 - form_adjustment)
        lambda_home = max(lambda_home, MIN_GOAL_RATE)
        lambda_away = max(lambda_away, MIN_GOAL_RATE)

        rho = max(min(inp.dixon_coles_rho, 0.2), -0.2)
        params = PoissonParams(lambda_home=lambda_home, lambda_away=lambda_away)
        return score_probabilities_dc(params, rho=rho)

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
        logits = logits_from_probabilities(probs)
        calibrated = self.calibrator.transform(logits)
        return calibrated / calibrated.sum(axis=1, keepdims=True)

    @staticmethod
    def _insert_margin(probabilities: Dict[str, float], target_overround: float = TARGET_OVERROUND) -> Dict[str, float]:
        """Apply bookmaker-style margin after calibration without changing beliefs."""
        fair = normalize_probabilities(probabilities)
        margin = max(target_overround - 1.0, 0.0)
        weights = {k: v ** 1.2 for k, v in fair.items()}
        weight_sum = sum(weights.values()) or 1.0
        priced = {k: fair[k] + margin * (weights[k] / weight_sum) for k in fair}
        return priced

    @staticmethod
    def _apply_risk_shading(
        priced_probabilities: Dict[str, float],
        exposure: Optional[Dict[str, float]],
        target_overround: float = TARGET_OVERROUND,
    ) -> Dict[str, float]:
        """Shift prices to manage liability while keeping beliefs unchanged."""
        if not exposure:
            return priced_probabilities
        total_liability = sum(abs(v) for v in exposure.values()) or 1.0
        adjustments = {
            k: max(0.05, 1.0 + RISK_SHADING_STRENGTH * (exposure.get(k, 0.0) / total_liability))
            for k in priced_probabilities
        }
        shaded = {k: max(priced_probabilities[k] * adjustments[k], 1e-6) for k in priced_probabilities}
        scale = target_overround / (sum(shaded.values()) or target_overround)
        return {k: v * scale for k, v in shaded.items()}

    def predict(self, inp: PredictionInput) -> Dict[str, object]:
        poisson_pred = self.poisson_prediction(inp)
        poisson_probs = poisson_pred.one_x_two

        components = [np.array([poisson_probs["home"], poisson_probs["draw"], poisson_probs["away"]])]
        weights = [1.0]

        market_probs = self.market_probabilities(inp.odds)
        if market_probs:
            market_weight = self._market_weight(market_probs)
            components.append(np.array([market_probs["home"], market_probs["draw"], market_probs["away"]]))
            weights = [1.0 - market_weight, market_weight]

        consensus_probs = self.consensus_probabilities(inp.bookmaker_lines)
        if consensus_probs:
            consensus_weight = self._market_weight(consensus_probs)
            components.append(np.array([consensus_probs["home"], consensus_probs["draw"], consensus_probs["away"]]))
            weights.append(consensus_weight)

        if self.ml_model:
            ml_probs = self._ml_view(inp, market_probs or poisson_probs)
            if ml_probs:
                components.append(np.array([ml_probs["home"], ml_probs["draw"], ml_probs["away"]]))
                weights.append(0.2)

        components = [component.ravel() for component in components]
        if self.stacking_model:
            stacked_inputs = [np.atleast_2d(component) for component in components]
            stacked = self.stacking_model.predict(stacked_inputs)[0]
            pooled = stacked
        else:
            pooled = linear_pool(components, weights)
        calibrated = self._calibrate(pooled.reshape(1, -1))[0]
        fair_probabilities = {"home": calibrated[0], "draw": calibrated[1], "away": calibrated[2]}
        if self.boosting_head:
            fair_probabilities = self.boosting_head.adjust(fair_probabilities)
        priced_probabilities = self._insert_margin(fair_probabilities, target_overround=TARGET_OVERROUND)
        shaded_probabilities = self._apply_risk_shading(priced_probabilities, inp.exposure, target_overround=TARGET_OVERROUND)
        final_odds = {k: 1.0 / v for k, v in shaded_probabilities.items()}
        resolved_odds = resolve_odds_from_sources(inp.odds, fair_probabilities, target_overround=TARGET_OVERROUND)
        confidence = 1.0 - market_entropy({"home": calibrated[0], "draw": calibrated[1], "away": calibrated[2]}) / np.log(3)
        result = {
            "fixture_id": inp.fixture_id,
            "probabilities": fair_probabilities,
            "priced_probabilities": priced_probabilities,
            "final_odds": final_odds,
            "resolved_odds": resolved_odds,
            "model_version": MODEL_VERSION,
            "confidence": confidence,
            "calibrated": True,
        }
        return result
