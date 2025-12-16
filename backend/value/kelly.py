"""Kelly staking utilities."""
from __future__ import annotations

from typing import Mapping


def kelly_fraction(prob: float, odds: float) -> float:
    if odds <= 1.0:
        raise ValueError("Odds must exceed 1.0")
    b = odds - 1
    return max(0.0, (prob * (b + 1) - 1) / b)


def fractional_kelly(prob: float, odds: float, fraction: float = 0.5) -> float:
    return kelly_fraction(prob, odds) * fraction


def portfolio_kelly(probs: Mapping[str, float], odds: Mapping[str, float], fraction: float = 0.5) -> Mapping[str, float]:
    return {k: fractional_kelly(probs[k], odds[k], fraction) for k in probs if k in odds}


