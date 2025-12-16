"""Brier score metric."""
from __future__ import annotations

import numpy as np


def brier_score(probs: np.ndarray, labels: np.ndarray) -> float:
    one_hot = np.eye(probs.shape[1])[labels]
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


