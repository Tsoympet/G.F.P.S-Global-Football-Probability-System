"""Linear pooling of probability distributions."""
from __future__ import annotations

from typing import Iterable, List
import numpy as np


def linear_pool(distributions: Iterable[np.ndarray], weights: Iterable[float]) -> np.ndarray:
    probs = np.stack(list(distributions))
    w = np.array(list(weights), dtype=float)
    if probs.shape[0] != w.shape[0]:
        raise ValueError("Distributions and weights must align")
    if np.any(w < 0):
        raise ValueError("Weights must be non-negative")
    w = w / w.sum() if w.sum() > 0 else np.ones_like(w) / len(w)
    pooled = (probs.T * w).T.sum(axis=0)
    pooled = pooled / pooled.sum()
    return pooled


