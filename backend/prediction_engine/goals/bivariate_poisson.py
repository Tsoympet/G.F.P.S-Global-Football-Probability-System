"""Bivariate Poisson goal model supporting covariance between teams."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import math
import numpy as np


@dataclass(frozen=True)
class BivariatePoissonParams:
    lambda_home: float
    lambda_away: float
    lambda_shared: float


def bivariate_score_matrix(params: BivariatePoissonParams, max_goals: int = 10) -> np.ndarray:
    """Compute score probabilities for the bivariate Poisson distribution."""

    matrix = np.zeros((max_goals + 1, max_goals + 1))
    exp_term = math.exp(-(params.lambda_home + params.lambda_away + params.lambda_shared))
    log_floor = -1e12

    def log_power(lmbda: float, power: int) -> float:
        if power == 0:
            return 0.0
        if lmbda <= 0:
            return log_floor
        return power * math.log(lmbda)

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            total = 0.0
            max_k = min(i, j)
            for k in range(max_k + 1):
                log_home = log_power(params.lambda_home, i - k) - math.lgamma(i - k + 1)
                log_away = log_power(params.lambda_away, j - k) - math.lgamma(j - k + 1)
                log_shared = log_power(params.lambda_shared, k) - math.lgamma(k + 1)
                log_term = log_home + log_away + log_shared
                total += math.exp(log_term)
            matrix[i, j] = exp_term * total
    matrix = matrix / matrix.sum()
    return matrix


@dataclass(frozen=True)
class BivariatePoissonPrediction:
    score_matrix: np.ndarray
    one_x_two: Dict[str, float]


def score_probabilities(params: BivariatePoissonParams, max_goals: int = 10) -> BivariatePoissonPrediction:
    """Compute scoreline and 1X2 probabilities for the bivariate Poisson model."""

    matrix = bivariate_score_matrix(params, max_goals=max_goals)
    return BivariatePoissonPrediction(score_matrix=matrix, one_x_two=one_x_two_from_matrix(matrix))


def one_x_two_from_matrix(matrix: np.ndarray) -> Dict[str, float]:
    home = float(matrix[np.triu_indices_from(matrix, k=1)].sum())
    draw = float(np.trace(matrix))
    away = float(matrix[np.tril_indices_from(matrix, k=-1)].sum())
    total = home + draw + away
    return {"home": home / total, "draw": draw / total, "away": away / total}
