"""Momentum index for in-play λ adjustment."""
from __future__ import annotations

from typing import Iterable
import numpy as np


def momentum_index(events: Iterable[str]) -> float:
    """Compute a simple momentum indicator based on recent events.

    Positive events for the home team increase the index; negative events for
    the home team decrease it. Values are clipped to [-1, 1].
    """

    score = 0
    for event in events:
        if event.startswith("home_goal"):
            score += 2
        elif event.startswith("away_goal"):
            score -= 2
        elif event.startswith("home_red"):
            score -= 1
        elif event.startswith("away_red"):
            score += 1
    return float(np.clip(score / 5.0, -1.0, 1.0))


def adjust_lambda(base_lambda: float, momentum: float) -> float:
    return base_lambda * (1 + 0.3 * momentum)


