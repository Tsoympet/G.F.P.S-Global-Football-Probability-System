"""Skellam distribution for goal differentials without SciPy dependency."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np


def poisson_pmf(lmbda: float, k: int) -> float:
    return float(np.exp(-lmbda) * (lmbda ** k) / np.math.factorial(k))


@dataclass(frozen=True)
class SkellamParams:
    lambda_home: float
    lambda_away: float


def skellam_probabilities(params: SkellamParams, max_goals: int = 10) -> Dict[str, float]:
    """Compute win/draw probabilities by convolving truncated Poisson pmfs."""

    home_probs = np.array([poisson_pmf(params.lambda_home, k) for k in range(max_goals + 1)])
    away_probs = np.array([poisson_pmf(params.lambda_away, k) for k in range(max_goals + 1)])
    matrix = np.outer(home_probs, away_probs)
    home = float(matrix[np.triu_indices_from(matrix, k=1)].sum())
    draw = float(np.trace(matrix))
    away = float(matrix[np.tril_indices_from(matrix, k=-1)].sum())
    total = home + draw + away
    return {"home": home / total, "draw": draw / total, "away": away / total}


