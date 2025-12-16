"""Implied probability utilities for bookmaker odds.

This module converts odds formats into implied probabilities and enforces
normalization constraints used throughout the modelling stack. All helpers
are deterministic and avoid in-place mutation so they can be unit tested
without fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Tuple
import math


@dataclass(frozen=True)
class OddsQuote:
    """Represents a single outcome's odds.

    Attributes:
        outcome: Canonical outcome label (e.g. "home", "draw", "away").
        decimal_odds: Decimal (European) odds quoted by the bookmaker.
    """

    outcome: str
    decimal_odds: float

    def implied_probability(self) -> float:
        """Return the naive implied probability from decimal odds.

        Decimal odds are inclusive of stake; the implied probability is the
        reciprocal. The caller is responsible for removing overround.
        """

        if self.decimal_odds <= 1.0:
            raise ValueError(f"Decimal odds must exceed 1.0, got {self.decimal_odds}")
        return 1.0 / self.decimal_odds


def decimal_to_implied(odds: Mapping[str, float]) -> Dict[str, float]:
    """Convert decimal odds mapping into implied probabilities.

    Args:
        odds: Mapping of outcome -> decimal odds.

    Returns:
        Mapping of outcome -> implied probability (unnormalized).
    """

    return {outcome: OddsQuote(outcome, price).implied_probability() for outcome, price in odds.items()}


def american_to_decimal(price: float) -> float:
    """Convert American odds (+200 / -150) to decimal odds.

    Follows the standard conversion used by regulated sportsbooks.
    """

    if price == 0:
        raise ValueError("American odds cannot be zero")
    if price > 0:
        return 1.0 + price / 100.0
    return 1.0 + 100.0 / abs(price)


def fractional_to_decimal(numerator: float, denominator: float) -> float:
    """Convert fractional odds (e.g. 5/2) to decimal odds."""

    if denominator <= 0:
        raise ValueError("Fractional odds denominator must be positive")
    return 1.0 + numerator / denominator


def normalize_probabilities(probs: Mapping[str, float]) -> Dict[str, float]:
    """Normalize probabilities to ensure they sum to one.

    Small numerical drift is handled by renormalizing; negative or zero values
    raise to avoid silently masking data issues.
    """

    total = sum(probs.values())
    if total <= 0:
        raise ValueError("Total probability must be positive")
    for key, value in probs.items():
        if value < 0:
            raise ValueError(f"Probability for {key} must be non-negative")
    return {k: v / total for k, v in probs.items()}


def implied_from_american(odds: Mapping[str, float]) -> Dict[str, float]:
    """Compute implied probabilities from American odds."""

    decimal_prices = {k: american_to_decimal(v) for k, v in odds.items()}
    return decimal_to_implied(decimal_prices)


def implied_from_fractional(quotes: Mapping[str, Tuple[float, float]]) -> Dict[str, float]:
    """Compute implied probabilities from fractional odds represented as (num, denom)."""

    decimal_prices = {k: fractional_to_decimal(num, denom) for k, (num, denom) in quotes.items()}
    return decimal_to_implied(decimal_prices)


def market_entropy(probs: Mapping[str, float]) -> float:
    """Compute Shannon entropy of the market probabilities.

    Entropy acts as a rough uncertainty measure of the quoted market.
    """

    normalized = normalize_probabilities(probs)
    return -sum(p * math.log(p) for p in normalized.values())


def price_spread(quotes: Iterable[OddsQuote]) -> float:
    """Return the spread between best and worst decimal odds for monitoring CLV."""

    decimals = [q.decimal_odds for q in quotes]
    if not decimals:
        return 0.0
    return max(decimals) - min(decimals)


