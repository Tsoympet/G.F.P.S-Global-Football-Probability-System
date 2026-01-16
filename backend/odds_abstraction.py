from __future__ import annotations

from typing import Dict, Optional


MIN_PROBABILITY = 1e-6
ODDS_DECIMAL_PLACES = 4


def _normalize_probabilities(probabilities: Dict[str, float]) -> Dict[str, float]:
    clamped = {k: max(v, MIN_PROBABILITY) for k, v in probabilities.items()}
    total = sum(clamped.values())
    if total == 0:
        raise ValueError("probability inputs must sum to a positive value")
    return {k: v / total for k, v in clamped.items()}


def resolve_odds_from_sources(
    provider_odds: Optional[Dict[str, float]],
    model_probabilities: Dict[str, float],
    target_overround: float = 1.04,
) -> Dict[str, float]:
    """Return bookmaker odds when available, otherwise fair odds from the model.

    Odds are derived as 1 / probability with a small configurable margin.
    """

    if provider_odds:
        return provider_odds

    fair = _normalize_probabilities(model_probabilities)
    base_odds = {k: 1.0 / v for k, v in fair.items()}
    margin_factor = max(target_overround, 1.0)
    return {k: round(base_odds[k] / margin_factor, ODDS_DECIMAL_PLACES) for k in base_odds}
