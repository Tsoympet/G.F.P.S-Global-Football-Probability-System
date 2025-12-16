"""Log loss scoring."""
from __future__ import annotations

import numpy as np


def log_loss(probs: np.ndarray, labels: np.ndarray) -> float:
    eps = 1e-15
    clipped = np.clip(probs, eps, 1 - eps)
    idx = (np.arange(len(labels)), labels)
    return float(-np.mean(np.log(clipped[idx])))


