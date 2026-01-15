"""Bayesian in-play update engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional
import numpy as np

from .time_decay import exponential_decay, linear_decay
from .momentum_index import adjust_lambda, momentum_index
from backend.prediction_engine.goals.poisson import PoissonParams, score_probabilities

MIN_CARD_FACTOR = 0.1
RED_CARD_LAMBDA_PENALTY = 0.2


@dataclass
class InPlayState:
    base_probs: Dict[str, float]
    elapsed_minutes: float
    home_goals: int
    away_goals: int


def goal_update(state: InPlayState, scoring_team: str) -> Dict[str, float]:
    """Update probabilities after a goal using Bayes' rule with simple likelihoods."""

    probs = state.base_probs
    if scoring_team == "home":
        likelihood = {"home": 1.6, "draw": 0.6, "away": 0.2}
    else:
        likelihood = {"home": 0.2, "draw": 0.6, "away": 1.6}
    posterior = {k: probs[k] * likelihood[k] for k in probs}
    total = sum(posterior.values())
    return {k: v / total for k, v in posterior.items()}


def card_update(state: InPlayState, team: str, red: bool = True) -> Dict[str, float]:
    """Adjust probabilities for cards; reds have stronger impact than yellows."""

    factor = 0.15 if red else 0.05
    probs = state.base_probs.copy()
    if team == "home":
        probs["home"] *= (1 - factor)
        probs["away"] *= (1 + factor)
    else:
        probs["away"] *= (1 - factor)
        probs["home"] *= (1 + factor)
    total = sum(probs.values())
    return {k: v / total for k, v in probs.items()}


def time_decay_adjustment(state: InPlayState, decay_half_life: float = 30.0) -> Dict[str, float]:
    decay = exponential_decay(state.elapsed_minutes, half_life=decay_half_life)
    probs = {k: state.base_probs[k] for k in state.base_probs}
    probs["draw"] += (1 - decay) * 0.05
    total = sum(probs.values())
    return {k: v / total for k, v in probs.items()}


@dataclass(frozen=True)
class InPlayContext:
    base_probs: Optional[Dict[str, float]]
    elapsed_minutes: float
    home_goals: int
    away_goals: int
    lambda_home: float
    lambda_away: float
    events: Iterable[str] = ()
    red_cards_home: int = 0
    red_cards_away: int = 0


def _outcome_from_matrix(matrix: np.ndarray, home_goals: int, away_goals: int) -> Dict[str, float]:
    home, draw, away = 0.0, 0.0, 0.0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            final_home = home_goals + i
            final_away = away_goals + j
            if final_home > final_away:
                home += matrix[i, j]
            elif final_home < final_away:
                away += matrix[i, j]
            else:
                draw += matrix[i, j]
    total = home + draw + away
    return {"home": home / total, "draw": draw / total, "away": away / total}


def update_in_play_probabilities(
    context: InPlayContext,
    max_goals: int = 6,
    red_card_penalty: float = RED_CARD_LAMBDA_PENALTY,
    min_card_factor: float = MIN_CARD_FACTOR,
) -> Dict[str, float]:
    """Update 1X2 probabilities during a match using Bayesian-style blending."""

    momentum = momentum_index(context.events)
    lambda_home = adjust_lambda(context.lambda_home, momentum)
    lambda_away = adjust_lambda(context.lambda_away, -momentum)
    card_factor_home = max(min_card_factor, 1.0 - red_card_penalty * context.red_cards_home)
    card_factor_away = max(min_card_factor, 1.0 - red_card_penalty * context.red_cards_away)
    lambda_home *= card_factor_home
    lambda_away *= card_factor_away

    remaining = linear_decay(context.elapsed_minutes)
    params = PoissonParams(lambda_home=lambda_home * remaining, lambda_away=lambda_away * remaining)
    prediction = score_probabilities(params, max_goals=max_goals)
    matrix = prediction.score_matrix
    live_probs = _outcome_from_matrix(matrix, context.home_goals, context.away_goals)

    if context.base_probs:
        decay = exponential_decay(context.elapsed_minutes)
        blended = {k: decay * context.base_probs[k] + (1 - decay) * live_probs[k] for k in live_probs}
        total = sum(blended.values())
        return {k: v / total for k, v in blended.items()}
    return live_probs
