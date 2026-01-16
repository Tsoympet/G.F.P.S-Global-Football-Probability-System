# Professional Analysis Engine

## Overview

The Analysis Engine generates deterministic, structured reports for bet slip simulations. Reports provide professional-grade analytical insights **without hype or encouragement to bet**.

## Purpose

Transform raw accumulator calculations into actionable intelligence:

1. **Executive Summary**: High-level metrics and key insight
2. **Selection Breakdown**: Per-selection analysis (odds, probability, EV, quality)
3. **Correlation Warnings**: Redundancy and contradiction detection
4. **Scenario Analysis**: Win requirements and failure points
5. **Professional Notes**: Market efficiency, timing, traps, opportunities

## Report Structure

### 1. Executive Summary

**Content**:
- Number of selections
- Combined odds (decimal)
- Combined probability (naive and correlation-adjusted)
- Expected value (naive and correlation-adjusted)
- Risk score [0, 1] and profile (low/medium/high)
- Key insight (one-line summary)

**Example Key Insight**:
> "3-leg accumulator; marginally positive expected value; medium risk; 1 significant correlation detected"

### 2. Selection Breakdown

For each selection:

**Fields**:
- Match (home vs away)
- Market and outcome
- Bookmaker odds
- Fair odds (computed from probability)
- Model probability
- Implied probability (from bookmaker odds)
- EV ROI
- Data quality (high/medium/low)
- Confidence (high/medium/low)
- Notes (list of analytical observations)

**Sample Notes**:
- "Probability computed from prediction engine"
- "High expected value (>10% ROI)"
- "Significant odds discrepancy (bookmaker: 2.00, fair: 2.08)"

### 3. Correlation Warnings

For each detected correlation:

**Fields**:
- Selection 1 & 2 keys
- Correlation type: "redundancy" or "contradiction"
- Severity: "critical" | "high" | "medium" | "low"
- Description (reason for correlation)
- Impact (explanation of effect on accumulator)

**Severity Mapping**:
- **Redundant** (ρ ≥ 0.6): Critical
- **Strong** (ρ ≥ 0.35): High
- **Moderate** (ρ ≥ 0.25): Medium
- **Weak** (ρ ≥ 0.15): Low

**Sample Impact**:
> "Severely inflated accumulator odds; combined probability is illusory"

### 4. Scenario Analysis

**Win Requirement**:
- Description: "All N selections must win for accumulator to pay out"
- Probability: Correlation-adjusted combined probability
- Impact: Comparison of naive vs adjusted probability

**Failure Points**:
- **Weakest Link**: Selection with lowest probability
  - Impact: "This selection has the lowest win probability (X%) and represents the primary failure risk"
- **Multi-leg Fragility** (if N ≥ 3): Probability of at least one loss
  - Impact: "Y% chance of accumulator loss due to multi-leg fragility"

### 5. Professional Notes

Categories:
- **market_efficiency**: Observations about odds pricing
- **timing**: Time-sensitive considerations
- **trap**: Warnings about common pitfalls
- **opportunity**: Potential value or inefficiency

**Sample Notes**:
- (**opportunity**) "Positive expected value suggests potential market inefficiency or favorable odds"
- (**trap**) "High correlation between selections creates EV illusion; naive accumulator calculation is misleading"
- (**timing**) "Odds may shift as fixtures approach; monitor for line movements and market updates"
- (**trap**) "High number of legs increases volatility and reduces win probability exponentially"

### 6. Disclaimer

Standard text (always included):

> "This analysis is for educational and informational purposes only. It does not constitute financial advice or an encouragement to gamble. All probability calculations are estimates based on statistical models and may not reflect actual outcomes. Gambling involves risk of loss. This is a SIMULATION/ANALYSIS tool only."

## Risk Scoring

### Volatility Score Calculation

**Formula**:
```
score = leg_factor + tail_factor + corr_factor + frag_factor
```

**Factors**:

1. **Leg Factor** (max 0.5):
   - `min(N / 10, 0.5)`
   - Increases with number of selections

2. **Tail Factor** (max 0.3):
   - 0.3 if P_combined < 0.1
   - 0.2 if P_combined < 0.25
   - 0.0 otherwise

3. **Correlation Factor** (max 0.15):
   - 0.15 if ρ_mean > 0.3
   - 0.05 if ρ_mean > 0.15
   - 0.0 otherwise

4. **Fragility Factor** (max 0.15):
   - 0.15 if weakest_prob < 0.3
   - 0.05 if weakest_prob < 0.5
   - 0.0 otherwise

**Risk Profile**:
- **High**: score ≥ 0.6
- **Medium**: score ≥ 0.3
- **Low**: score < 0.3

**Drivers**: List of factors contributing to risk (e.g., "High number of legs (5)", "Low combined probability (8.2%)")

## Tone and Style

### Principles

1. **Professional**: Analytical, data-driven, objective
2. **No Hype**: Avoid sensationalism or exaggeration
3. **No Encouragement**: Never suggest placing bets
4. **Educational**: Explain concepts and trade-offs
5. **Transparent**: Acknowledge limitations and assumptions

### Prohibited Language

❌ "Great opportunity!"
❌ "Sure thing"
❌ "Can't miss"
❌ "Guaranteed profit"
❌ "Hot tip"

### Preferred Language

✅ "Positive expected value suggests potential market inefficiency"
✅ "Correlation reduces true combined probability"
✅ "This analysis is for educational purposes only"
✅ "Probabilities are estimates and may not reflect actual outcomes"

## Implementation Details

### Location

`backend/analysis/report_engine.py`

### Key Functions

- `generate_professional_report(...)`: Main entry point
- `_analyze_selection(...)`: Per-selection analysis
- `_generate_correlation_warnings(...)`: Correlation → warnings mapping
- `_generate_scenario_analysis(...)`: Win/failure scenarios
- `_generate_professional_notes(...)`: Market/timing/trap notes
- `_generate_key_insight(...)`: One-line summary

### Data Flow

1. Analysis API receives request
2. Resolves probabilities and computes EVs
3. Detects correlations
4. Calculates accumulator totals (naive + adjusted)
5. Computes risk score
6. Calls `generate_professional_report(...)`
7. Returns structured JSON report

## Output Schema

```typescript
{
  executiveSummary: {
    num_selections: number;
    combined_odds: number;
    combined_probability_naive: number;
    combined_probability_adjusted: number;
    expected_value_naive: number;
    expected_value_adjusted: number;
    risk_score: number;
    risk_profile: string;
    key_insight: string;
  };
  selectionBreakdown: SelectionAnalysis[];
  correlationWarnings: CorrelationWarning[];
  scenarioAnalysis: ScenarioPoint[];
  professionalNotes: ProfessionalNote[];
  disclaimer: string;
}
```

## Use Cases

### High Correlation Warning

**Input**: 2 selections, same match, BTTS + Over
**Output**: 
- Correlation warning: "strong" severity
- Impact: "Accumulator probability is overstated; effective odds are lower than naive calculation"
- Professional note (trap): "High correlation between selections creates EV illusion"

### Low Probability Alert

**Input**: 5-leg accumulator, P_combined = 0.08
**Output**:
- Risk profile: "high"
- Tail factor: 0.3
- Scenario: "Probability of at least one selection failing: 92%"
- Professional note (trap): "High number of legs increases volatility"

### Positive EV Opportunity

**Input**: 2 selections, EV_adjusted = +0.06
**Output**:
- Professional note (opportunity): "Positive expected value suggests potential market inefficiency"
- Executive summary: "2-leg accumulator; positive expected value; low risk"

## Limitations

### What This Engine Does NOT Do

1. **Machine Learning**: No ML-based insights; purely deterministic
2. **Predictions**: Does not predict match outcomes beyond model probabilities
3. **Betting Advice**: Never recommends placing bets
4. **Real-Time Updates**: Static analysis of current state
5. **Historical Context**: No historical performance tracking

### Known Approximations

- Risk score is heuristic, not empirically calibrated
- Professional notes are rule-based, not context-aware
- Market efficiency comments are generic, not league/team-specific

## Validation

### Tests

See `backend/tests/test_analysis_report.py`:
- Report structure completeness
- Required keys presence
- Correlation warning generation
- Scenario analysis generation
- Professional notes generation

### Quality Checks

- All reports include disclaimer
- Executive summary always has key_insight
- Correlation warnings sorted by severity
- Risk profile matches score thresholds

## Future Enhancements (Not Implemented)

This documentation describes what IS implemented. Future versions may include:

- **Historical analysis tracking**: Compare predictions to actual outcomes
- **Personalized insights**: Adapt notes to user preferences
- **Export formats**: PDF, HTML, detailed CSV
- **ML-based insights**: Use ML to generate context-aware observations

## Disclaimer

This analysis engine is **deterministic and rule-based**. It provides consistent, reproducible reports but may not capture all nuances of real-world betting markets.

Use for **educational purposes only**. Do not treat as financial advice or betting recommendations.
