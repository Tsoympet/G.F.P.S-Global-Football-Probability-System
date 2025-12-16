"""Isotonic regression calibration."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from sklearn.isotonic import IsotonicRegression


@dataclass
class IsotonicCalibrator:
    models: list

    @classmethod
    def fit(cls, probs: np.ndarray, labels: np.ndarray) -> "IsotonicCalibrator":
        models = []
        for k in range(probs.shape[1]):
            ir = IsotonicRegression(out_of_bounds="clip")
            ir.fit(probs[:, k], (labels == k).astype(float))
            models.append(ir)
        return cls(models=models)

    def transform(self, probs: np.ndarray) -> np.ndarray:
        calibrated = np.zeros_like(probs)
        for k, model in enumerate(self.models):
            calibrated[:, k] = model.transform(probs[:, k])
        calibrated = calibrated / calibrated.sum(axis=1, keepdims=True)
        return calibrated


