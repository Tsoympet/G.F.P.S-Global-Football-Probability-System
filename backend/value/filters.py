"""Filters for controlling value bet selection."""
from __future__ import annotations

from typing import Mapping


def apply_threshold(values: Mapping[str, float], min_ev: float = 0.0) -> Mapping[str, float]:
    return {k: v for k, v in values.items() if v >= min_ev}


def cap_stake(stakes: Mapping[str, float], cap: float) -> Mapping[str, float]:
    return {k: min(v, cap) for k, v in stakes.items()}


