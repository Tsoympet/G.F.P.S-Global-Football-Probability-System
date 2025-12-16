"""Probability edge calculations."""
from __future__ import annotations

from typing import Mapping


def edge(prob: float, market_prob: float) -> float:
    if not 0 <= prob <= 1 or not 0 <= market_prob <= 1:
        raise ValueError("Probabilities must be within [0,1]")
    return prob - market_prob


def edges(probabilities: Mapping[str, float], market_probs: Mapping[str, float]) -> Mapping[str, float]:
    return {k: edge(probabilities[k], market_probs[k]) for k in probabilities if k in market_probs}


