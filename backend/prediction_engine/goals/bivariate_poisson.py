"""Bivariate Poisson goal model supporting covariance between teams."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np


@dataclass(frozen=True)
class BivariatePoissonParams:
    lambda_home: float
    lambda_away: float
    lambda_shared: float


def bivariate_score_matrix(params: BivariatePoissonParams, max_goals: int = 10) -> np.ndarray:
    """Compute score probabilities for the bivariate Poisson distribution."""

    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            term = 0.0
            max_k = min(i, j)
            for k in range(max_k + 1):
                coeff = np.exp(- (params.lambda_home + params.lambda_away + params.lambda_shared))
                coeff *= (params.lambda_home ** (i - k)) / np.math.factorial(i - k)
                coeff *= (params.lambda_away ** (j - k)) / np.math.factorial(j - k)
                coeff *= (params.lambda_shared ** k) / np.math.factorial(k)
                coeff *= np.math.factorial(i) * np.math.factorial(j) / (
                    np.math.factorial(k) * np.math.factorial(i - k) * np.math.factorial(j - k)
                )
                term += coeff
            matrix[i, j] = term
    matrix = matrix / matrix.sum()
    return matrix


def one_x_two_from_matrix(matrix: np.ndarray) -> Dict[str, float]:
    home = float(matrix[np.triu_indices_from(matrix, k=1)].sum())
    draw = float(np.trace(matrix))
    away = float(matrix[np.tril_indices_from(matrix, k=-1)].sum())
    total = home + draw + away
    return {"home": home / total, "draw": draw / total, "away": away / total}


