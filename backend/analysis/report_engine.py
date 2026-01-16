"""
Professional Analysis Report Engine (deterministic report generation).
Generates structured, analytical reports for bet slip simulations.
"""
from __future__ import annotations

from typing import List, Dict, Any, Literal, Optional
from dataclasses import dataclass

from backend.correlation.engine import Selection, CorrelationResult


@dataclass
class SelectionAnalysis:
    """Analysis for a single selection."""
    selection_key: str
    match: str
    market: str
    outcome: str
    odds_bookmaker: float
    odds_fair: Optional[float]
    probability: float
    ev_roi: float
    data_quality: str  # "high" | "medium" | "low"
    confidence: str  # "high" | "medium" | "low"
    notes: List[str]


@dataclass
class CorrelationWarning:
    """Warning about correlation between selections."""
    selection1_key: str
    selection2_key: str
    correlation_type: Literal["redundancy", "contradiction"]
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    impact: str


@dataclass
class ScenarioPoint:
    """Key scenario in accumulator analysis."""
    scenario_type: Literal["win_requirement", "failure_point"]
    description: str
    probability: float
    impact: str


@dataclass
class ProfessionalNote:
    """Professional analytical note."""
    category: Literal["market_efficiency", "timing", "trap", "opportunity"]
    note: str


@dataclass
class AnalysisReport:
    """Complete professional analysis report."""
    executive_summary: Dict[str, Any]
    selection_breakdown: List[SelectionAnalysis]
    correlation_warnings: List[CorrelationWarning]
    scenario_analysis: List[ScenarioPoint]
    professional_notes: List[ProfessionalNote]
    disclaimer: str


def _analyze_selection(
    selection: Selection,
    odds_fair: Optional[float],
    prob: float,
    ev_roi: float
) -> SelectionAnalysis:
    """Analyze a single selection."""
    notes = []
    
    # Data quality assessment
    data_quality = "high"
    confidence = "high"
    
    if not selection.fixture_id:
        data_quality = "medium"
        notes.append("No fixture ID provided, using manual input")
    
    if not selection.prob:
        notes.append("Probability computed from prediction engine")
    else:
        notes.append("Probability provided by client")
    
    # EV assessment
    if ev_roi > 0.10:
        notes.append("High expected value (>10% ROI)")
    elif ev_roi > 0.05:
        notes.append("Good expected value (>5% ROI)")
    elif ev_roi > 0:
        notes.append("Marginal positive expected value")
    elif ev_roi > -0.05:
        notes.append("Slightly negative expected value")
    else:
        notes.append("Negative expected value (<-5% ROI)")
        confidence = "low"
    
    # Odds comparison
    if odds_fair and abs(selection.odds - odds_fair) / odds_fair > 0.15:
        notes.append(f"Significant odds discrepancy (bookmaker: {selection.odds:.2f}, fair: {odds_fair:.2f})")
    
    return SelectionAnalysis(
        selection_key=selection.client_selection_key,
        match=f"{selection.home_team} vs {selection.away_team}",
        market=f"{selection.market_name} - {selection.outcome}",
        outcome=selection.outcome,
        odds_bookmaker=selection.odds,
        odds_fair=odds_fair,
        probability=prob,
        ev_roi=ev_roi,
        data_quality=data_quality,
        confidence=confidence,
        notes=notes
    )


def _generate_correlation_warnings(
    correlations: List[CorrelationResult],
    selections_map: Dict[str, Selection]
) -> List[CorrelationWarning]:
    """Generate correlation warnings from detected correlations."""
    warnings = []
    
    for corr in correlations:
        s1 = selections_map.get(corr.selection1_key)
        s2 = selections_map.get(corr.selection2_key)
        
        if not s1 or not s2:
            continue
        
        # Determine type and severity
        if corr.classification == "redundant":
            corr_type = "redundancy"
            severity = "critical"
            impact = "Severely inflated accumulator odds; combined probability is illusory"
        elif corr.classification == "strong":
            corr_type = "redundancy"
            severity = "high"
            impact = "Accumulator probability is overstated; effective odds are lower than naive calculation"
        elif corr.classification == "moderate":
            corr_type = "redundancy"
            severity = "medium"
            impact = "Moderate correlation reduces true accumulator probability"
        else:
            corr_type = "redundancy"
            severity = "low"
            impact = "Weak correlation; minimal impact on accumulator calculation"
        
        # Negative correlations indicate contradictions
        if corr.coefficient < 0:
            corr_type = "contradiction"
            severity = "medium" if abs(corr.coefficient) > 0.25 else "low"
            impact = "Selections may be mutually exclusive or contradictory; scenario tension"
        
        warnings.append(CorrelationWarning(
            selection1_key=corr.selection1_key,
            selection2_key=corr.selection2_key,
            correlation_type=corr_type,
            severity=severity,
            description=corr.reason,
            impact=impact
        ))
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    warnings.sort(key=lambda w: severity_order[w.severity])
    
    return warnings


def _generate_scenario_analysis(
    selections: List[Selection],
    combined_prob_naive: float,
    combined_prob_corr: float,
    num_selections: int
) -> List[ScenarioPoint]:
    """Generate scenario analysis (win requirements and failure points)."""
    scenarios = []
    
    # Win requirement
    scenarios.append(ScenarioPoint(
        scenario_type="win_requirement",
        description=f"All {num_selections} selections must win for accumulator to pay out",
        probability=combined_prob_corr,
        impact=f"Correlation-adjusted win probability: {combined_prob_corr*100:.2f}% (naive: {combined_prob_naive*100:.2f}%)"
    ))
    
    # Key failure point - weakest link
    if selections:
        # Find selection with lowest probability
        weakest = min(selections, key=lambda s: s.prob or 0.5)
        weakest_prob = weakest.prob or 0.5
        scenarios.append(ScenarioPoint(
            scenario_type="failure_point",
            description=f"Weakest link: {weakest.home_team} vs {weakest.away_team} - {weakest.outcome}",
            probability=weakest_prob,
            impact=f"This selection has the lowest win probability ({weakest_prob*100:.1f}%) and represents the primary failure risk"
        ))
    
    # Accumulator fragility
    if num_selections >= 3:
        # Probability at least one loses
        prob_at_least_one_loss = 1.0 - combined_prob_corr
        scenarios.append(ScenarioPoint(
            scenario_type="failure_point",
            description=f"Probability of at least one selection failing",
            probability=prob_at_least_one_loss,
            impact=f"{prob_at_least_one_loss*100:.1f}% chance of accumulator loss due to multi-leg fragility"
        ))
    
    return scenarios


def _generate_professional_notes(
    selections: List[Selection],
    combined_ev_corr: float,
    has_high_correlation: bool
) -> List[ProfessionalNote]:
    """Generate professional analytical notes."""
    notes = []
    
    # Market efficiency note
    if combined_ev_corr > 0.05:
        notes.append(ProfessionalNote(
            category="opportunity",
            note="Positive expected value suggests potential market inefficiency or favorable odds"
        ))
    elif combined_ev_corr < -0.10:
        notes.append(ProfessionalNote(
            category="market_efficiency",
            note="Negative expected value indicates efficient market pricing or unfavorable odds"
        ))
    
    # Correlation trap
    if has_high_correlation:
        notes.append(ProfessionalNote(
            category="trap",
            note="High correlation between selections creates EV illusion; naive accumulator calculation is misleading"
        ))
    
    # Timing note
    if any(s.start_time for s in selections):
        notes.append(ProfessionalNote(
            category="timing",
            note="Odds may shift as fixtures approach; monitor for line movements and market updates"
        ))
    
    # Multi-leg risk
    if len(selections) >= 5:
        notes.append(ProfessionalNote(
            category="trap",
            note="High number of legs increases volatility and reduces win probability exponentially"
        ))
    
    return notes


def generate_professional_report(
    selections: List[Selection],
    selection_analyses: List[SelectionAnalysis],
    correlations: List[CorrelationResult],
    combined_odds: float,
    combined_prob_naive: float,
    combined_prob_corr: float,
    combined_ev_naive: float,
    combined_ev_corr: float,
    risk_score: float,
    risk_profile: str
) -> AnalysisReport:
    """
    Generate complete professional analysis report.
    
    Tone: professional, analytical, no hype, no encouragement to bet.
    """
    selections_map = {s.client_selection_key: s for s in selections}
    
    # Executive Summary
    executive_summary = {
        "num_selections": len(selections),
        "combined_odds": round(combined_odds, 2),
        "combined_probability_naive": round(combined_prob_naive, 4),
        "combined_probability_adjusted": round(combined_prob_corr, 4),
        "expected_value_naive": round(combined_ev_naive, 4),
        "expected_value_adjusted": round(combined_ev_corr, 4),
        "risk_score": round(risk_score, 2),
        "risk_profile": risk_profile,
        "key_insight": _generate_key_insight(
            len(selections),
            combined_ev_corr,
            risk_profile,
            len([c for c in correlations if c.classification in ["strong", "redundant"]])
        )
    }
    
    # Correlation Warnings
    warnings = _generate_correlation_warnings(correlations, selections_map)
    
    # Scenario Analysis
    scenarios = _generate_scenario_analysis(
        selections,
        combined_prob_naive,
        combined_prob_corr,
        len(selections)
    )
    
    # Professional Notes
    has_high_corr = any(c.classification in ["strong", "redundant"] for c in correlations)
    prof_notes = _generate_professional_notes(selections, combined_ev_corr, has_high_corr)
    
    # Disclaimer
    disclaimer = (
        "This analysis is for educational and informational purposes only. "
        "It does not constitute financial advice or an encouragement to gamble. "
        "All probability calculations are estimates based on statistical models and may not reflect actual outcomes. "
        "Gambling involves risk of loss. This is a SIMULATION/ANALYSIS tool only."
    )
    
    return AnalysisReport(
        executive_summary=executive_summary,
        selection_breakdown=selection_analyses,
        correlation_warnings=warnings,
        scenario_analysis=scenarios,
        professional_notes=prof_notes,
        disclaimer=disclaimer
    )


def _generate_key_insight(
    num_selections: int,
    ev_corr: float,
    risk_profile: str,
    num_high_correlations: int
) -> str:
    """Generate key insight summary."""
    insights = []
    
    # Selections count
    if num_selections == 1:
        insights.append("Single selection")
    elif num_selections <= 3:
        insights.append(f"{num_selections}-leg accumulator")
    else:
        insights.append(f"{num_selections}-leg accumulator with high complexity")
    
    # EV assessment
    if ev_corr > 0.05:
        insights.append("positive expected value")
    elif ev_corr > 0:
        insights.append("marginally positive expected value")
    else:
        insights.append("negative expected value")
    
    # Risk
    insights.append(f"{risk_profile} risk")
    
    # Correlations
    if num_high_correlations > 0:
        insights.append(f"{num_high_correlations} significant correlation(s) detected")
    
    return "; ".join(insights)
