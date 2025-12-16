"""Temperature scaling for multiclass logits without external optimizers."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def _nll(temp: float, logits: np.ndarray, labels: np.ndarray) -> float:
    scaled = logits / temp
    log_probs = scaled - np.log(np.sum(np.exp(scaled), axis=1, keepdims=True))
    idx = (np.arange(len(labels)), labels)
    return float(-np.mean(log_probs[idx]))


def _grid_search_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    candidates = np.linspace(0.05, 5.0, 50)
    losses = [_nll(t, logits, labels) for t in candidates]
    best_idx = int(np.argmin(losses))
    return float(candidates[best_idx])


@dataclass
class TemperatureScaler:
    temperature: float

    @classmethod
    def fit(cls, logits: np.ndarray, labels: np.ndarray) -> "TemperatureScaler":
        temp = _grid_search_temperature(logits, labels)
        return cls(temperature=temp)

    def transform(self, logits: np.ndarray) -> np.ndarray:
        scaled = logits / self.temperature
        exps = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))
        probs = exps / np.sum(exps, axis=1, keepdims=True)
        return probs


