"""Overround and vigorish calculations."""
from __future__ import annotations

from typing import Dict, Mapping

from .implied_probability import decimal_to_implied, normalize_probabilities


def overround_from_odds(odds: Mapping[str, float]) -> float:
    """Compute the bookmaker's overround from decimal odds."""

    implied = decimal_to_implied(odds)
    return max(0.0, sum(implied.values()) - 1.0)


def fair_probs_from_overround(odds: Mapping[str, float]) -> Dict[str, float]:
    """Remove overround by scaling probabilities to sum to one."""

    implied = decimal_to_implied(odds)
    return normalize_probabilities(implied)


def margin_percentage(odds: Mapping[str, float]) -> float:
    """Return the vigorish as a percentage of total implied probability."""

    implied = decimal_to_implied(odds)
    implied_total = sum(implied.values())
    return (implied_total - 1.0) / implied_total if implied_total else 0.0


