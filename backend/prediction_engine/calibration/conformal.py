"""Conformal prediction utilities for probabilistic sets."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class ConformalPredictor:
    quantile: float

    def predict_set(self, probs: np.ndarray) -> np.ndarray:
        """Return confidence sets given calibrated probabilities."""

        sorted_probs = np.sort(probs, axis=1)[:, ::-1]
        cumulative = np.cumsum(sorted_probs, axis=1)
        threshold = np.quantile(1 - cumulative[:, -1], self.quantile)
        return (probs >= threshold).astype(int)


