"""Line movement and CLV feature computation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import numpy as np

from .implied_probability import normalize_probabilities


@dataclass(frozen=True)
class LineObservation:
    minute: float
    price: float


def implied_path(observations: Iterable[LineObservation]) -> List[float]:
    """Return the sequence of implied probabilities from price observations."""

    path = []
    for obs in sorted(observations, key=lambda o: o.minute):
        if obs.price <= 1.0:
            continue
        path.append(1.0 / obs.price)
    return path


def volatility(observations: Iterable[LineObservation]) -> float:
    """Compute standard deviation of the implied probability path."""

    path = implied_path(observations)
    return float(np.std(path)) if path else 0.0


def closing_line_value(open_price: float, close_price: float, model_prob: float) -> float:
    """Compute CLV defined as model edge against closing odds vs open odds."""

    if open_price <= 1.0 or close_price <= 1.0:
        raise ValueError("Prices must exceed 1.0")
    open_prob = 1.0 / open_price
    close_prob = 1.0 / close_price
    fair_prob = model_prob
    return (fair_prob - close_prob) - (fair_prob - open_prob)


def drift(observations: Iterable[LineObservation]) -> float:
    """Signed drift between first and last implied probabilities."""

    path = implied_path(observations)
    if len(path) < 2:
        return 0.0
    return path[-1] - path[0]


