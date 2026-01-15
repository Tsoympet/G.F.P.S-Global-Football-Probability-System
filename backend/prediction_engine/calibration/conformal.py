"""Conformal prediction utilities for probabilistic sets."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ConformalPredictor:
    """Split-conformal predictor for multiclass probability outputs."""

    threshold: float

    @classmethod
    def fit(cls, probs: np.ndarray, labels: np.ndarray, alpha: float = 0.1) -> "ConformalPredictor":
        """Fit a conformal predictor using nonconformity scores.

        Args:
            probs: Calibrated probabilities of shape (n_samples, n_classes).
            labels: True labels encoded as class indices.
            alpha: Miscoverage level; 0.1 yields 90% confidence sets.
        """

        if probs.size == 0:
            return cls(threshold=1.0)
        n = probs.shape[0]
        nonconformity = 1.0 - probs[np.arange(n), labels]
        sorted_scores = np.sort(nonconformity)
        k = int(np.ceil((n + 1) * (1 - alpha))) - 1
        k = max(0, min(k, n - 1))
        return cls(threshold=float(sorted_scores[k]))

    def predict_set(self, probs: np.ndarray) -> np.ndarray:
        """Return confidence sets given calibrated probabilities.

        Returns:
            Binary array shaped (n_samples, n_classes) with 1 indicating
            membership of the prediction set for each class.
        """

        return (1.0 - probs <= self.threshold).astype(int)
