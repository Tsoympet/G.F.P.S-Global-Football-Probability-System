"""Stacked ensemble for 1X2 probabilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass
class StackingEnsemble:
    meta: LogisticRegression

    @classmethod
    def fit(cls, base_outputs: Iterable[np.ndarray], labels: np.ndarray) -> "StackingEnsemble":
        X = np.hstack(list(base_outputs))
        meta = LogisticRegression(max_iter=200, multi_class="multinomial")
        meta.fit(X, labels)
        return cls(meta=meta)

    def predict(self, base_outputs: Iterable[np.ndarray]) -> np.ndarray:
        X = np.hstack(list(base_outputs))
        probs = self.meta.predict_proba(X)
        return probs / probs.sum(axis=1, keepdims=True)


