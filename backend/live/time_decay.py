"""Time decay functions for in-play updates."""
from __future__ import annotations

import math


def exponential_decay(elapsed_minutes: float, half_life: float = 30.0) -> float:
    if half_life <= 0:
        raise ValueError("Half-life must be positive")
    return math.exp(-math.log(2) * elapsed_minutes / half_life)


def linear_decay(elapsed_minutes: float, total_minutes: float = 90.0) -> float:
    remaining = max(total_minutes - elapsed_minutes, 0.0)
    return remaining / total_minutes


