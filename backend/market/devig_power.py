"""Power method margin removal.

The power method assumes a homogeneous margin across outcomes and raises
probabilities to a power to enforce normalization after removing the vigorish.
"""
from __future__ import annotations

from typing import Dict, Mapping
import math

from .implied_probability import decimal_to_implied, normalize_probabilities


def power_devig(odds: Mapping[str, float], power: float = 1.0) -> Dict[str, float]:
    """Apply a power transform to remove overround.

    Args:
        odds: Mapping of outcome -> decimal odds.
        power: Exponent to apply to implied probabilities before renormalizing.

    Returns:
        Fair outcome probabilities summing to one.
    """

    if power <= 0:
        raise ValueError("Power must be positive")
    implied = decimal_to_implied(odds)
    adjusted = {k: v ** power for k, v in implied.items()}
    return normalize_probabilities(adjusted)


def infer_power_for_margin(odds: Mapping[str, float]) -> float:
    """Heuristically solve for the power that removes margin.

    Uses a binary search on the exponent so that the transformed probabilities
    sum to one, bounded to a reasonable interval for stability.
    """

    implied = decimal_to_implied(odds)
    target = 1.0
    low, high = 0.1, 5.0
    for _ in range(30):
        mid = 0.5 * (low + high)
        total = sum(v ** mid for v in implied.values())
        if total > target:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


