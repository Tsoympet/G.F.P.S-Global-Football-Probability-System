"""Weighted bookmaker consensus calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping
import numpy as np

from .implied_probability import normalize_probabilities, decimal_to_implied


@dataclass(frozen=True)
class BookmakerLine:
    name: str
    odds: Mapping[str, float]
    weight: float = 1.0

    def implied_probs(self) -> Dict[str, float]:
        return decimal_to_implied(self.odds)


def consensus_probabilities(lines: Iterable[BookmakerLine]) -> Dict[str, float]:
    """Aggregate multiple bookmaker lines into a weighted consensus."""

    totals: Dict[str, float] = {}
    total_weight = 0.0
    for line in lines:
        weight = max(line.weight, 0.0)
        implied = line.implied_probs()
        for outcome, prob in implied.items():
            totals[outcome] = totals.get(outcome, 0.0) + weight * prob
        total_weight += weight
    if total_weight == 0:
        return normalize_probabilities({k: v for k, v in totals.items()}) if totals else {}
    averaged = {k: v / total_weight for k, v in totals.items()}
    return normalize_probabilities(averaged)


def market_entropy_weight(line: BookmakerLine) -> float:
    """Compute an entropy-based quality weight (lower entropy => sharper)."""

    probs = line.implied_probs()
    probs = normalize_probabilities(probs)
    entropy = -sum(p * np.log(p) for p in probs.values())
    max_entropy = np.log(len(probs)) if probs else 1.0
    return 1.0 - entropy / max_entropy


def weighted_by_sharpness(lines: Iterable[BookmakerLine]) -> Dict[str, float]:
    """Consensus with dynamic weights derived from entropy (sharpness)."""

    weighted_lines = []
    for line in lines:
        w = market_entropy_weight(line)
        weighted_lines.append(BookmakerLine(name=line.name, odds=line.odds, weight=w))
    return consensus_probabilities(weighted_lines)


