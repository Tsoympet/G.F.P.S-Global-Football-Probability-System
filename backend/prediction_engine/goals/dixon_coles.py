"""Dixon-Coles adjustment for low-scoring dependency."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np

from .poisson import PoissonParams, PoissonPrediction, score_probabilities, poisson_pmf


def dixon_coles_correlation(lambda_home: float, lambda_away: float, rho: float) -> np.ndarray:
    """Apply Dixon-Coles correlation adjustment for low scores."""

    adjust = np.ones((2, 2))
    adjust[0, 0] = 1 - (lambda_home * lambda_away) * rho
    adjust[0, 1] = 1 + lambda_home * rho
    adjust[1, 0] = 1 + lambda_away * rho
    adjust[1, 1] = 1 - rho
    return adjust


def score_probabilities_dc(params: PoissonParams, rho: float = 0.0, max_goals: int = 10) -> PoissonPrediction:
    """Compute score probabilities with Dixon-Coles dependence structure."""

    base = score_probabilities(params, max_goals)
    matrix = base.score_matrix.copy()
    adjust = dixon_coles_correlation(params.lambda_home, params.lambda_away, rho)
    matrix[:2, :2] *= adjust
    total_mass = matrix.sum()
    matrix = matrix / total_mass
    one_x_two = {
        "home": float(matrix[np.triu_indices_from(matrix, k=1)].sum()),
        "draw": float(np.trace(matrix)),
        "away": float(matrix[np.tril_indices_from(matrix, k=-1)].sum()),
    }
    return PoissonPrediction(score_matrix=matrix, one_x_two=one_x_two)


def log_likelihood_dc(home_goals: int, away_goals: int, params: PoissonParams, rho: float) -> float:
    """Log-likelihood of a single outcome under the Dixon-Coles model."""

    base = poisson_pmf(params.lambda_home, home_goals) * poisson_pmf(params.lambda_away, away_goals)
    if home_goals <= 1 and away_goals <= 1:
        adjust = dixon_coles_correlation(params.lambda_home, params.lambda_away, rho)
        weight = adjust[home_goals, away_goals]
    else:
        weight = 1.0
    prob = base * weight
    return float(np.log(prob + 1e-12))


