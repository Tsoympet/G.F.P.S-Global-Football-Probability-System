"""Temperature scaling for multiclass logits without external optimizers."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def _log_softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    return shifted - np.log(np.sum(np.exp(shifted), axis=1, keepdims=True))


def _nll(temp: float, logits: np.ndarray, labels: np.ndarray) -> float:
    scaled = logits / temp
    log_probs = _log_softmax(scaled)
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
        scaled = logits / max(self.temperature, 1e-6)
        log_probs = _log_softmax(scaled)
        return np.exp(log_probs)


def logits_from_probabilities(probs: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Convert probabilities into logit-like scores for calibration."""

    clipped = np.clip(probs, eps, 1.0)
    return np.log(clipped)

