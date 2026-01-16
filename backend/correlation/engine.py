"""
Correlation detection engine (heuristic-v1) for bet slip analysis.
Detects correlations between selections to adjust accumulator probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Literal, Optional


@dataclass
class Selection:
    """Represents a single bet selection."""
    client_selection_key: str
    fixture_id: Optional[str]
    home_team: str
    away_team: str
    league: str
    start_time: Optional[datetime]
    market_type: str
    market_name: str
    outcome: str
    odds: float
    prob: Optional[float] = None


@dataclass
class CorrelationResult:
    """Correlation between two selections."""
    selection1_key: str
    selection2_key: str
    coefficient: float  # [-1, 1]
    classification: Literal["weak", "moderate", "strong", "redundant"]
    reason: str
    
    @property
    def abs_coefficient(self) -> float:
        return abs(self.coefficient)


# Classification thresholds
WEAK_THRESHOLD = 0.15
MODERATE_THRESHOLD = 0.25
STRONG_THRESHOLD = 0.35
REDUNDANT_THRESHOLD = 0.6

# Same-team exposure window (default 7 days)
SAME_TEAM_WINDOW_DAYS = 7


def _classify_correlation(rho: float) -> Literal["weak", "moderate", "strong", "redundant"]:
    """Classify correlation coefficient into strength categories."""
    abs_rho = abs(rho)
    if abs_rho >= REDUNDANT_THRESHOLD:
        return "redundant"
    if abs_rho >= STRONG_THRESHOLD:
        return "strong"
    if abs_rho >= MODERATE_THRESHOLD:
        return "moderate"
    return "weak"


def _normalize_market_type(market: str) -> str:
    """Normalize market type names for comparison."""
    lower = (market or "").lower()
    if lower in {"1x2", "match winner", "match winner 1x2", "match_result"}:
        return "1x2"
    if "over/under" in lower or "total" in lower or "over_under" in lower:
        return "totals"
    if "asian" in lower or "handicap" in lower:
        return "handicap"
    if "both teams" in lower or "btts" in lower:
        return "btts"
    return "other"


def _same_match_correlation(s1: Selection, s2: Selection) -> Optional[CorrelationResult]:
    """
    Detect correlation between two selections on the same match.
    
    Rules:
    - 1X2 ↔ Over/Under: moderate positive correlation
    - BTTS ↔ Over: strong positive correlation
    - Asian Handicap ↔ Match Result: strong positive correlation
    """
    # Must be same fixture
    if s1.fixture_id != s2.fixture_id or not s1.fixture_id:
        return None
    
    # Same exact market and outcome = redundant (should be caught earlier)
    if s1.market_name == s2.market_name and s1.outcome == s2.outcome:
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.95,
            classification="redundant",
            reason="Same market and outcome on same match (duplicate selection)"
        )
    
    market1 = _normalize_market_type(s1.market_type)
    market2 = _normalize_market_type(s2.market_type)
    
    # 1X2 ↔ Over/Under
    if {market1, market2} == {"1x2", "totals"}:
        # Home/Away wins tend to correlate with higher totals
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.30,
            classification="moderate",
            reason="1X2 outcome and Over/Under on same match have moderate correlation"
        )
    
    # BTTS ↔ Over
    if {market1, market2} == {"btts", "totals"}:
        # BTTS=Yes correlates strongly with Over
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.55,
            classification="strong",
            reason="BTTS and Over/Under on same match have strong correlation"
        )
    
    # Handicap ↔ Match Result
    if {market1, market2} == {"handicap", "1x2"}:
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.60,
            classification="strong",
            reason="Asian Handicap and Match Result on same match are strongly correlated"
        )
    
    # Same match but different uncorrelated markets
    if market1 != market2:
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.10,
            classification="weak",
            reason=f"Different markets ({market1}, {market2}) on same match have weak correlation"
        )
    
    return None


def _same_team_correlation(s1: Selection, s2: Selection) -> Optional[CorrelationResult]:
    """
    Detect correlation between selections involving the same team across different matches.
    Short-window shared exposure heuristic.
    """
    # Must be different fixtures
    if s1.fixture_id == s2.fixture_id:
        return None
    
    # Check if any team overlaps
    teams1 = {s1.home_team, s1.away_team}
    teams2 = {s2.home_team, s2.away_team}
    shared_teams = teams1 & teams2
    
    if not shared_teams:
        return None
    
    # Check time window
    if s1.start_time and s2.start_time:
        time_diff = abs(s1.start_time - s2.start_time)
        if time_diff > timedelta(days=SAME_TEAM_WINDOW_DAYS):
            return None
    
    # Same team in close time window
    team_name = ", ".join(sorted(shared_teams))
    return CorrelationResult(
        selection1_key=s1.client_selection_key,
        selection2_key=s2.client_selection_key,
        coefficient=0.20,
        classification="weak",
        reason=f"Shared team ({team_name}) across matches within {SAME_TEAM_WINDOW_DAYS} days"
    )


def _same_league_correlation(s1: Selection, s2: Selection) -> Optional[CorrelationResult]:
    """
    Detect correlation between selections in the same league.
    Low-priority heuristic for league-wide patterns.
    """
    # Must be different fixtures
    if s1.fixture_id == s2.fixture_id:
        return None
    
    # Same league
    if s1.league != s2.league:
        return None
    
    # Very weak correlation for same league totals patterns
    market1 = _normalize_market_type(s1.market_type)
    market2 = _normalize_market_type(s2.market_type)
    
    if market1 == market2 == "totals":
        return CorrelationResult(
            selection1_key=s1.client_selection_key,
            selection2_key=s2.client_selection_key,
            coefficient=0.05,
            classification="weak",
            reason=f"Same league ({s1.league}) totals patterns have very weak correlation"
        )
    
    return None


def detect_correlations(selections: List[Selection]) -> List[CorrelationResult]:
    """
    Detect pairwise correlations between all selections.
    
    Returns list of correlation results with coefficients in [-1, 1].
    Only returns correlations that meet minimum threshold (>= WEAK_THRESHOLD).
    """
    correlations: List[CorrelationResult] = []
    
    for i, s1 in enumerate(selections):
        for j, s2 in enumerate(selections):
            if i >= j:  # Only check each pair once
                continue
            
            # Check for same match correlations (highest priority)
            corr = _same_match_correlation(s1, s2)
            if corr and corr.abs_coefficient >= WEAK_THRESHOLD:
                correlations.append(corr)
                continue
            
            # Check for same team correlations
            corr = _same_team_correlation(s1, s2)
            if corr and corr.abs_coefficient >= WEAK_THRESHOLD:
                correlations.append(corr)
                continue
            
            # Check for same league correlations (lowest priority)
            corr = _same_league_correlation(s1, s2)
            if corr and corr.abs_coefficient >= WEAK_THRESHOLD:
                correlations.append(corr)
                continue
    
    return correlations


def compute_effective_legs(
    num_selections: int,
    correlations: List[CorrelationResult],
    alpha: float = 1.0
) -> tuple[float, float]:
    """
    Compute effective number of legs using correlation adjustment.
    
    Method: effective-legs-v1
    - Compute weighted mean of positive correlations (ρ+)
    - N_eff = N / (1 + α * ρ+_mean * (N-1))
    - Returns (N_eff, ρ+_mean)
    
    Args:
        num_selections: Number of selections in accumulator
        correlations: List of pairwise correlations
        alpha: Adjustment factor (default 1.0)
    
    Returns:
        (effective_legs, positive_corr_mean)
    """
    if num_selections <= 1:
        return float(num_selections), 0.0
    
    # Collect positive correlations
    positive_corrs = [c.coefficient for c in correlations if c.coefficient > 0]
    
    if not positive_corrs:
        # No positive correlations, legs are independent
        return float(num_selections), 0.0
    
    # Weighted mean of positive correlations
    rho_plus_mean = sum(positive_corrs) / len(positive_corrs)
    
    # Effective legs formula
    denominator = 1.0 + alpha * rho_plus_mean * (num_selections - 1)
    n_eff = num_selections / denominator
    
    return n_eff, rho_plus_mean
