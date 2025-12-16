"""Expected calibration error and related utilities."""
from __future__ import annotations

import numpy as np


def expected_calibration_error(probs: np.ndarray, labels: np.ndarray, bins: int = 10) -> float:
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    bin_edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for i in range(bins):
        mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
        if not np.any(mask):
            continue
        bin_conf = np.mean(confidences[mask])
        bin_acc = np.mean(predictions[mask] == labels[mask])
        ece += np.abs(bin_conf - bin_acc) * np.mean(mask)
    return float(ece)


