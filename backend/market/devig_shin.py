"""Shin method for removing insider-trading bias from odds.

Implements the Shin (1992) model, which estimates the proportion of insider
money to adjust the bookmaker margin asymmetrically across outcomes.
"""
from __future__ import annotations

from typing import Dict, Mapping
import math

from .implied_probability import decimal_to_implied, normalize_probabilities


def _solve_shin_z(implied: Mapping[str, float]) -> float:
    low, high = 0.0, 0.25  # realistic range for z share of insider trading
    for _ in range(40):
        mid = 0.5 * (low + high)
        denom = sum(math.sqrt(p + mid) for p in implied.values())
        est_sum = sum((math.sqrt(p + mid) - mid) / denom for p in implied.values())
        if est_sum > 1.0:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


def shin_probabilities(odds: Mapping[str, float]) -> Dict[str, float]:
    """Return fair probabilities using the Shin method."""

    implied = decimal_to_implied(odds)
    z = _solve_shin_z(implied)
    denom = sum(math.sqrt(p + z) for p in implied.values())
    fair = {k: (math.sqrt(v + z) - z) / denom for k, v in implied.items()}
    return normalize_probabilities(fair)


