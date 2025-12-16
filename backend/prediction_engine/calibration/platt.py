"""Platt scaling for multiclass probabilities via one-vs-rest logistic models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass
class PlattScaler:
    model: LogisticRegression

    @classmethod
    def fit(cls, logits: np.ndarray, labels: np.ndarray) -> "PlattScaler":
        """Fit a one-vs-rest logistic regression calibrator."""

        lr = LogisticRegression(max_iter=100, multi_class="ovr")
        lr.fit(logits, labels)
        return cls(model=lr)

    def transform(self, logits: np.ndarray) -> np.ndarray:
        """Return calibrated probabilities."""

        return self.model.predict_proba(logits)


