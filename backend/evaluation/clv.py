"""Closing line value calculations."""
from __future__ import annotations

from typing import Mapping, Optional


def clv_odds_space(opening_odds: float, closing_odds: float) -> float:
    """
    CLV in odds space: (O0 / Oc) - 1
    """
    if opening_odds <= 0 or closing_odds <= 0:
        raise ValueError("Odds must be positive")
    return (opening_odds / closing_odds) - 1.0


def clv_probability_space(opening_odds: float, closing_odds: float) -> float:
    """
    CLV in implied probability space: (1/Oc) - (1/O0)
    """
    if opening_odds <= 0 or closing_odds <= 0:
        raise ValueError("Odds must be positive")
    return (1.0 / closing_odds) - (1.0 / opening_odds)


def beat_closing_line(opening_odds: float, closing_odds: float) -> bool:
    """
    Returns True when the bettor received a better price than the close.
    """
    if opening_odds <= 0 or closing_odds <= 0:
        return False
    return opening_odds > closing_odds


def clv_summary(opening_odds: Optional[float], closing_odds: Optional[float]) -> Mapping[str, Optional[float]]:
    if opening_odds is None or closing_odds is None:
        return {"clv_odds": None, "clv_prob": None, "beat_closing": None}
    return {
        "clv_odds": clv_odds_space(opening_odds, closing_odds),
        "clv_prob": clv_probability_space(opening_odds, closing_odds),
        "beat_closing": beat_closing_line(opening_odds, closing_odds),
    }


def portfolio_clv(model_probs: Mapping[str, float], closing_odds: Mapping[str, float]) -> Mapping[str, float]:
    """
    Legacy helper maintained for compatibility: expected edge vs closing odds.
    """
    return {
        k: model_probs[k] * (closing_odds[k] - 1) - (1 - model_probs[k])
        for k in model_probs
        if k in closing_odds
    }
