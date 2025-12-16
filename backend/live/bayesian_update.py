"""Bayesian in-play update engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np

from .time_decay import exponential_decay


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


