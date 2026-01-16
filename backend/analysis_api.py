"""
Bet Slip Analysis API.
POST /analysis/betslip - Analyze bet slip with correlation-aware accumulator calculations.

This endpoint operates in SIMULATION/ANALYSIS mode only - no bet execution.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import List, Optional, Literal, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session

from backend.auth_dependency import require_user
from backend.correlation.engine import (
    Selection,
    detect_correlations,
    compute_effective_legs,
)
from backend.analysis.report_engine import (
    generate_professional_report,
    _analyze_selection,
)
from backend.db import SessionLocal
from backend.models import User
from backend.prediction_engine import predict_market
from backend.stats_context import build_poisson_context
from backend.validation import require_decimal_odds, parse_iso_datetime
from backend.value.ev import expected_value


router = APIRouter(prefix="/analysis", tags=["analysis"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Request/Response Schemas
# ============================================================================


class SelectionIn(BaseModel):
    """Individual selection in bet slip."""
    clientSelectionKey: constr(min_length=1)
    serverSelectionId: Optional[str] = None
    fixtureId: Optional[str] = None
    homeTeam: constr(min_length=1)
    awayTeam: constr(min_length=1)
    league: constr(min_length=1)
    leagueId: Optional[str] = None
    startTime: Optional[str] = None  # ISO datetime
    marketType: constr(min_length=1)
    marketName: constr(min_length=1)
    line: Optional[float] = None
    outcome: constr(min_length=1)
    oddsBookmaker: float = Field(gt=1.0)
    oddsFair: Optional[float] = Field(default=None, gt=1.0)
    modelProbability: Optional[float] = Field(default=None, gt=0.0, lt=1.0)


class BetSlipAnalysisRequest(BaseModel):
    """Request schema for bet slip analysis."""
    schemaVersion: str = "1.0"
    slipId: constr(min_length=1)
    mode: Literal["single", "accumulator"] = "accumulator"
    selections: List[SelectionIn] = Field(min_items=1)
    correlationAlpha: float = Field(default=1.0, ge=0.0, le=2.0)


class SelectionResult(BaseModel):
    """Analysis result for individual selection."""
    clientSelectionKey: str
    match: str
    market: str
    outcome: str
    oddsBookmaker: float
    oddsFair: Optional[float]
    probability: float
    impliedProbability: Optional[float]
    evRoi: float
    dataQuality: str
    confidence: str
    notes: List[str]


class CorrelationPair(BaseModel):
    """Pairwise correlation result."""
    selection1Key: str
    selection2Key: str
    coefficient: float
    classification: str
    reason: str


class RiskMetrics(BaseModel):
    """Risk and volatility metrics."""
    score: float  # [0, 1]
    profile: str  # "low" | "medium" | "high"
    drivers: List[str]


class SlipTotals(BaseModel):
    """Accumulator totals."""
    combinedOddsDecimal: float
    combinedProbability: Dict[str, float]  # {naiveIndependence, correlationAdjusted}
    expectedValueRoi: Dict[str, float]  # {naive, correlationAdjusted}
    overroundStackingRisk: Dict[str, Any]
    effectiveLegs: Optional[float] = None
    volatilityMetrics: RiskMetrics


class CorrelationWarningOut(BaseModel):
    """Correlation warning."""
    selection1Key: str
    selection2Key: str
    correlationType: str
    severity: str
    description: str
    impact: str


class ScenarioPointOut(BaseModel):
    """Scenario analysis point."""
    scenarioType: str
    description: str
    probability: float
    impact: str


class ProfessionalNoteOut(BaseModel):
    """Professional note."""
    category: str
    note: str


class AnalysisReportOut(BaseModel):
    """Professional analysis report sections."""
    executiveSummary: Dict[str, Any]
    selectionBreakdown: List[SelectionResult]
    correlationWarnings: List[CorrelationWarningOut]
    scenarioAnalysis: List[ScenarioPointOut]
    professionalNotes: List[ProfessionalNoteOut]
    disclaimer: str


class BetSlipAnalysisResponse(BaseModel):
    """Response schema for bet slip analysis."""
    ok: bool
    slipId: str
    mode: str
    numSelections: int
    selections: List[SelectionResult]
    correlations: List[CorrelationPair]
    totals: SlipTotals
    report: AnalysisReportOut
    metadata: Dict[str, Any]


# ============================================================================
# Helper Functions
# ============================================================================


def _parse_start_time(raw: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(parse_iso_datetime(raw).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _compute_implied_probability(odds: float) -> float:
    """Compute implied probability from decimal odds."""
    if odds <= 1.0:
        return 0.0
    try:
        return 1.0 / odds
    except (ZeroDivisionError, ValueError):
        return 0.0


def _resolve_probability(
    selection: SelectionIn,
    db: Session
) -> tuple[float, Optional[float]]:
    """
    Resolve probability for a selection.
    
    Returns: (probability, fair_odds)
    """
    # Use provided probability if valid
    if selection.modelProbability and 0 < selection.modelProbability < 1:
        prob = selection.modelProbability
        # Estimate fair odds from probability
        fair_odds = 1.0 / prob if prob > 0 else None
        return prob, fair_odds
    
    # Otherwise, compute via prediction engine
    league_id = selection.leagueId or selection.league
    ctx = build_poisson_context(db, league_id, selection.homeTeam, selection.awayTeam)
    
    # Add fixture context
    ctx["fixture_id"] = selection.fixtureId or "analysis"
    ctx["home_team"] = selection.homeTeam
    ctx["away_team"] = selection.awayTeam
    ctx["league"] = selection.league
    
    preds = predict_market(
        selection.marketName,
        {selection.outcome: selection.oddsBookmaker},
        ctx,
    )
    
    info = preds.get(selection.outcome)
    if not info:
        raise HTTPException(
            422,
            f"Unable to compute probability for outcome '{selection.outcome}' in market '{selection.marketName}'"
        )
    
    prob = info["prob"]
    ev = info["ev"]
    
    # Estimate fair odds from probability
    fair_odds = 1.0 / prob if prob > 0 else None
    
    return prob, fair_odds


def _estimate_overround_stacking(
    selections: List[SelectionIn],
    probabilities: List[float]
) -> Dict[str, Any]:
    """
    Estimate overround stacking risk.
    
    Limited implementation: can only estimate when sufficient market info is available.
    """
    # Simple heuristic: compare implied probability sum to model probability sum
    implied_sum = sum(_compute_implied_probability(s.oddsBookmaker) for s in selections)
    model_sum = sum(probabilities)
    
    if len(selections) == 0:
        return {
            "estimated": False,
            "note": "No selections to analyze"
        }
    
    # Overround per selection (rough estimate)
    avg_implied = implied_sum / len(selections)
    avg_model = model_sum / len(selections)
    
    overround_factor = avg_implied / avg_model if avg_model > 0 else 1.0
    
    # Accumulator overround compounds
    compound_overround = overround_factor ** len(selections)
    
    return {
        "estimated": True,
        "compoundOverroundFactor": round(compound_overround, 4),
        "averageImpliedProbability": round(avg_implied, 4),
        "averageModelProbability": round(avg_model, 4),
        "note": f"Estimated compound overround factor: {compound_overround:.2f}x across {len(selections)} selections",
        "limitation": "Overround calculation is approximate; true bookmaker margins vary by market and selection"
    }


def _compute_volatility_score(
    num_selections: int,
    combined_prob: float,
    correlation_mean: float,
    weakest_prob: float
) -> tuple[float, str, List[str]]:
    """
    Compute volatility/risk proxy score.
    
    Returns: (score [0,1], risk_profile, drivers[])
    
    Factors:
    - Number of legs (more legs = higher volatility)
    - Combined probability tail risk (low prob = high risk)
    - Correlation concentration (high correlation = risk adjustment)
    - Probability fragility (weakest link)
    """
    drivers = []
    score = 0.0
    
    # Factor 1: Number of legs
    leg_factor = min(num_selections / 10.0, 0.5)  # Max 0.5 contribution
    score += leg_factor
    if num_selections >= 5:
        drivers.append(f"High number of legs ({num_selections})")
    
    # Factor 2: Combined probability tail risk
    if combined_prob < 0.1:
        tail_factor = 0.3
        drivers.append(f"Very low combined probability ({combined_prob*100:.1f}%)")
    elif combined_prob < 0.25:
        tail_factor = 0.2
        drivers.append(f"Low combined probability ({combined_prob*100:.1f}%)")
    else:
        tail_factor = 0.0
    score += tail_factor
    
    # Factor 3: Correlation concentration
    if correlation_mean > 0.3:
        corr_factor = 0.15
        drivers.append(f"High average correlation ({correlation_mean:.2f})")
    elif correlation_mean > 0.15:
        corr_factor = 0.05
    else:
        corr_factor = 0.0
    score += corr_factor
    
    # Factor 4: Probability fragility (weakest link)
    if weakest_prob < 0.3:
        frag_factor = 0.15
        drivers.append(f"Weak link with low probability ({weakest_prob*100:.1f}%)")
    elif weakest_prob < 0.5:
        frag_factor = 0.05
    else:
        frag_factor = 0.0
    score += frag_factor
    
    # Normalize to [0, 1]
    score = min(score, 1.0)
    
    # Classify risk profile
    if score >= 0.6:
        risk_profile = "high"
    elif score >= 0.3:
        risk_profile = "medium"
    else:
        risk_profile = "low"
    
    if not drivers:
        drivers.append("Standard risk factors")
    
    return score, risk_profile, drivers


# ============================================================================
# Main Endpoint
# ============================================================================


@router.post("/betslip")
def analyze_betslip(
    request: BetSlipAnalysisRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db)
) -> BetSlipAnalysisResponse:
    """
    Analyze bet slip with correlation-aware accumulator calculations.
    
    SIMULATION/ANALYSIS MODE ONLY - No bet execution.
    
    Validates odds, resolves probabilities, computes EV, detects correlations,
    and generates professional analysis report.
    """
    if not request.selections:
        raise HTTPException(400, "No selections provided")
    
    # ========================================================================
    # Process Each Selection
    # ========================================================================
    
    selections_data: List[Selection] = []
    selection_results: List[SelectionResult] = []
    probabilities: List[float] = []
    evs: List[float] = []
    fair_odds_list: List[Optional[float]] = []
    
    for sel_in in request.selections:
        # Validate odds
        try:
            odds_bookmaker = require_decimal_odds(sel_in.oddsBookmaker, "oddsBookmaker")
        except ValueError as e:
            raise HTTPException(422, f"Invalid odds for {sel_in.clientSelectionKey}: {e}")
        
        # Resolve probability
        prob, fair_odds = _resolve_probability(sel_in, db)
        
        # Compute EV
        ev_roi = expected_value(prob, odds_bookmaker)
        
        # Compute implied probability
        implied_prob = _compute_implied_probability(odds_bookmaker)
        
        # Create Selection object for correlation detection
        selection_obj = Selection(
            client_selection_key=sel_in.clientSelectionKey,
            fixture_id=sel_in.fixtureId,
            home_team=sel_in.homeTeam,
            away_team=sel_in.awayTeam,
            league=sel_in.league,
            start_time=_parse_start_time(sel_in.startTime),
            market_type=sel_in.marketType,
            market_name=sel_in.marketName,
            outcome=sel_in.outcome,
            odds=odds_bookmaker,
            prob=prob
        )
        selections_data.append(selection_obj)
        
        # Analyze selection
        sel_analysis = _analyze_selection(selection_obj, fair_odds, prob, ev_roi)
        
        # Build result
        selection_results.append(SelectionResult(
            clientSelectionKey=sel_in.clientSelectionKey,
            match=f"{sel_in.homeTeam} vs {sel_in.awayTeam}",
            market=f"{sel_in.marketName} - {sel_in.outcome}",
            outcome=sel_in.outcome,
            oddsBookmaker=odds_bookmaker,
            oddsFair=fair_odds,
            probability=round(prob, 4),
            impliedProbability=round(implied_prob, 4),
            evRoi=round(ev_roi, 4),
            dataQuality=sel_analysis.data_quality,
            confidence=sel_analysis.confidence,
            notes=sel_analysis.notes
        ))
        
        probabilities.append(prob)
        evs.append(ev_roi)
        fair_odds_list.append(fair_odds)
    
    # ========================================================================
    # Detect Correlations
    # ========================================================================
    
    correlations = detect_correlations(selections_data)
    
    correlation_pairs = [
        CorrelationPair(
            selection1Key=c.selection1_key,
            selection2Key=c.selection2_key,
            coefficient=round(c.coefficient, 4),
            classification=c.classification,
            reason=c.reason
        )
        for c in correlations
    ]
    
    # ========================================================================
    # Compute Accumulator Totals
    # ========================================================================
    
    num_selections = len(request.selections)
    
    # Combined odds (product)
    combined_odds = math.prod(sel.oddsBookmaker for sel in request.selections)
    
    # Combined probability - naive independence
    combined_prob_naive = math.prod(probabilities)
    
    # Combined probability - correlation adjusted
    n_eff, corr_mean = compute_effective_legs(num_selections, correlations, request.correlationAlpha)
    
    if num_selections > 1 and n_eff > 0:
        # P_corr = P_naive^(N/N_eff)
        exponent = num_selections / n_eff
        combined_prob_corr = combined_prob_naive ** exponent
    else:
        combined_prob_corr = combined_prob_naive
        n_eff = float(num_selections)
        corr_mean = 0.0
    
    # Expected value - naive
    ev_naive = expected_value(combined_prob_naive, combined_odds)
    
    # Expected value - correlation adjusted
    ev_corr = expected_value(combined_prob_corr, combined_odds)
    
    # Overround stacking risk
    overround_risk = _estimate_overround_stacking(request.selections, probabilities)
    
    # Volatility / risk score
    weakest_prob = min(probabilities) if probabilities else 0.5
    risk_score, risk_profile, risk_drivers = _compute_volatility_score(
        num_selections,
        combined_prob_corr,
        corr_mean,
        weakest_prob
    )
    
    # Build totals
    totals = SlipTotals(
        combinedOddsDecimal=round(combined_odds, 2),
        combinedProbability={
            "naiveIndependence": round(combined_prob_naive, 6),
            "correlationAdjusted": round(combined_prob_corr, 6)
        },
        expectedValueRoi={
            "naive": round(ev_naive, 4),
            "correlationAdjusted": round(ev_corr, 4)
        },
        overroundStackingRisk=overround_risk,
        effectiveLegs=round(n_eff, 2) if num_selections > 1 else None,
        volatilityMetrics=RiskMetrics(
            score=round(risk_score, 2),
            profile=risk_profile,
            drivers=risk_drivers
        )
    )
    
    # ========================================================================
    # Generate Professional Report
    # ========================================================================
    
    report = generate_professional_report(
        selections=selections_data,
        selection_analyses=[
            _analyze_selection(selections_data[i], fair_odds_list[i], probabilities[i], evs[i])
            for i in range(len(selections_data))
        ],
        correlations=correlations,
        combined_odds=combined_odds,
        combined_prob_naive=combined_prob_naive,
        combined_prob_corr=combined_prob_corr,
        combined_ev_naive=ev_naive,
        combined_ev_corr=ev_corr,
        risk_score=risk_score,
        risk_profile=risk_profile
    )
    
    # Convert report to output schema
    report_out = AnalysisReportOut(
        executiveSummary=report.executive_summary,
        selectionBreakdown=selection_results,
        correlationWarnings=[
            CorrelationWarningOut(
                selection1Key=w.selection1_key,
                selection2Key=w.selection2_key,
                correlationType=w.correlation_type,
                severity=w.severity,
                description=w.description,
                impact=w.impact
            )
            for w in report.correlation_warnings
        ],
        scenarioAnalysis=[
            ScenarioPointOut(
                scenarioType=s.scenario_type,
                description=s.description,
                probability=round(s.probability, 4),
                impact=s.impact
            )
            for s in report.scenario_analysis
        ],
        professionalNotes=[
            ProfessionalNoteOut(
                category=n.category,
                note=n.note
            )
            for n in report.professional_notes
        ],
        disclaimer=report.disclaimer
    )
    
    # ========================================================================
    # Build Response
    # ========================================================================
    
    return BetSlipAnalysisResponse(
        ok=True,
        slipId=request.slipId,
        mode=request.mode,
        numSelections=num_selections,
        selections=selection_results,
        correlations=correlation_pairs,
        totals=totals,
        report=report_out,
        metadata={
            "schemaVersion": request.schemaVersion,
            "correlationAlpha": request.correlationAlpha,
            "effectiveLegs": round(n_eff, 2) if num_selections > 1 else None,
            "correlationMean": round(corr_mean, 4) if num_selections > 1 else 0.0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
