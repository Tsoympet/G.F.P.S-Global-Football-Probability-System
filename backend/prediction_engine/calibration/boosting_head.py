from __future__ import annotations

import os
from typing import Dict, Optional

from backend.market.implied_probability import normalize_probabilities


def _parse_offsets(raw: str) -> Dict[str, float]:
    offsets: Dict[str, float] = {}
    if not raw:
        return offsets
    for token in raw.split(","):
        if ":" not in token:
            continue
        key, val = token.split(":", 1)
        key = key.strip().lower()
        try:
            offsets[key] = float(val)
        except ValueError:
            continue
    return offsets


class BoostingCalibrationHead:
    """
    Lightweight boosting-style calibration head that gently nudges class
    probabilities using small residual-style offsets and then re-normalizes.
    """

    def __init__(self, learning_rate: float = 0.05, offsets: Optional[Dict[str, float]] = None) -> None:
        self.learning_rate = learning_rate
        self.offsets = offsets or {}

    def adjust(self, probs: Dict[str, float], residuals: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        updates = dict(self.offsets)
        if residuals:
            for k, v in residuals.items():
                updates[k] = updates.get(k, 0.0) + v

        adjusted = {}
        for key, base_prob in probs.items():
            adjusted_val = base_prob + self.learning_rate * updates.get(key, 0.0)
            adjusted[key] = max(adjusted_val, 0.0)
        return normalize_probabilities(adjusted)


def load_boosting_head() -> Optional[BoostingCalibrationHead]:
    enabled = os.getenv("BOOSTING_HEAD_ENABLED", "false").lower() in {"1", "true", "yes"}
    if not enabled:
        return None
    lr = float(os.getenv("BOOSTING_HEAD_LR", "0.05"))
    offsets = _parse_offsets(os.getenv("BOOSTING_HEAD_OFFSETS", "home:0.02,draw:0.0,away:-0.02"))
    return BoostingCalibrationHead(learning_rate=lr, offsets=offsets)
