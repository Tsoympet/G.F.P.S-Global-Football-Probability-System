"""Canonical Poisson goal model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np


@dataclass(frozen=True)
class PoissonParams:
    lambda_home: float
    lambda_away: float


@dataclass(frozen=True)
class PoissonPrediction:
    score_matrix: np.ndarray
    one_x_two: Dict[str, float]


def poisson_pmf(lmbda: float, k: int) -> float:
    return float(np.exp(-lmbda) * (lmbda ** k) / np.math.factorial(k))


def score_probabilities(params: PoissonParams, max_goals: int = 10) -> PoissonPrediction:
    """Compute scoreline probabilities under independent Poisson assumptions."""

    home_range = np.arange(0, max_goals + 1)
    away_range = np.arange(0, max_goals + 1)
    home_pmf = np.array([poisson_pmf(params.lambda_home, k) for k in home_range])
    away_pmf = np.array([poisson_pmf(params.lambda_away, k) for k in away_range])
    matrix = np.outer(home_pmf, away_pmf)
    one_x_two = {
        "home": float(matrix[np.triu_indices_from(matrix, k=1)].sum()),
        "draw": float(np.trace(matrix)),
        "away": float(matrix[np.tril_indices_from(matrix, k=-1)].sum()),
    }
    total = sum(one_x_two.values())
    if total == 0:
        raise ValueError("Degenerate probability mass")
    one_x_two = {k: v / total for k, v in one_x_two.items()}
    return PoissonPrediction(score_matrix=matrix, one_x_two=one_x_two)


def estimate_from_history(home_goals: Tuple[int, ...], away_goals: Tuple[int, ...]) -> PoissonParams:
    """Estimate lambdas as empirical means with Laplace smoothing."""

    if len(home_goals) != len(away_goals):
        raise ValueError("Goal history must align")
    n = len(home_goals)
    smooth = 1.0
    lambda_home = (sum(home_goals) + smooth) / (n + smooth)
    lambda_away = (sum(away_goals) + smooth) / (n + smooth)
    return PoissonParams(lambda_home=lambda_home, lambda_away=lambda_away)


