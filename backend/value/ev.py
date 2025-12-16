"""Expected value calculations for betting opportunities."""
from __future__ import annotations

from typing import Mapping


def expected_value(prob: float, decimal_odds: float) -> float:
    if not 0 <= prob <= 1:
        raise ValueError("Probability must be within [0, 1]")
    if decimal_odds <= 1.0:
        raise ValueError("Decimal odds must exceed 1.0")
    return prob * (decimal_odds - 1) - (1 - prob)


def portfolio_ev(probs: Mapping[str, float], odds: Mapping[str, float]) -> Mapping[str, float]:
    return {k: expected_value(probs[k], odds[k]) for k in probs if k in odds}


