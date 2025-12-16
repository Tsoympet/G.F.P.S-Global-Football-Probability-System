"""Closing line value calculations."""
from __future__ import annotations

from typing import Mapping


def clv(model_prob: float, closing_odds: float, stake: float = 1.0) -> float:
    if closing_odds <= 1.0:
        raise ValueError("Closing odds must exceed 1.0")
    edge = model_prob * (closing_odds - 1) - (1 - model_prob)
    return edge * stake


def portfolio_clv(model_probs: Mapping[str, float], closing_odds: Mapping[str, float]) -> Mapping[str, float]:
    return {k: clv(model_probs[k], closing_odds[k]) for k in model_probs if k in closing_odds}


