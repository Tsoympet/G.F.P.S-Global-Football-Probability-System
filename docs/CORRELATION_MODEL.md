# Correlation Detection Model (Heuristic v1)

## Overview

The correlation detection engine identifies relationships between bet slip selections that affect accumulator probability calculations. This is version 1, using **deterministic heuristic rules** rather than machine learning.

## Purpose

When combining multiple selections into an accumulator, naive independence (multiplying individual probabilities) overestimates the true combined probability if selections are correlated. The correlation engine:

1. Detects pairwise correlations between selections
2. Classifies correlation strength (weak, moderate, strong, redundant)
3. Provides explanations for detected correlations
4. Adjusts accumulator probability via effective-legs method

## Correlation Detection Rules

### Same Match Correlations

When two selections are on the **same fixture** (same fixture ID):

#### 1. Same Market & Outcome (Redundant)
- **Coefficient**: 0.95
- **Classification**: Redundant
- **Example**: Both selections are "Team A to win" in Match Winner market
- **Impact**: Duplicate selection; extremely high correlation

#### 2. 1X2 ↔ Over/Under
- **Coefficient**: 0.30
- **Classification**: Moderate
- **Reasoning**: Home/Away wins tend to correlate with higher scoring
- **Example**: "Home Win" + "Over 2.5 goals"

#### 3. BTTS ↔ Over/Under
- **Coefficient**: 0.55
- **Classification**: Strong
- **Reasoning**: Both Teams To Score (Yes) strongly implies higher total goals
- **Example**: "BTTS Yes" + "Over 2.5 goals"

#### 4. Asian Handicap ↔ Match Result (1X2)
- **Coefficient**: 0.60
- **Classification**: Strong
- **Reasoning**: Handicap outcomes highly correlated with outright winner
- **Example**: "Home -0.5 (AH)" + "Home Win"

#### 5. Different Uncorrelated Markets
- **Coefficient**: 0.10
- **Classification**: Weak
- **Reasoning**: Default weak correlation for same match, different market types
- **Example**: "1X2" + "Player Props"

### Same Team Across Matches

When selections involve the **same team in different matches**:

- **Coefficient**: 0.20
- **Classification**: Weak
- **Time Window**: Within 7 days (configurable: `SAME_TEAM_WINDOW_DAYS`)
- **Reasoning**: Team form and morale create short-term shared exposure
- **Example**: "Team A to win vs Team B" + "Team A to win vs Team C" (within 7 days)

### Same League Patterns

When selections are in the **same league** (different matches):

- **Coefficient**: 0.05
- **Classification**: Weak
- **Applies to**: Totals markets only
- **Reasoning**: League-wide scoring patterns create very weak correlation
- **Example**: "Match 1 Over 2.5" + "Match 2 Over 2.5" in same league

## Classification Thresholds

```
|ρ| >= 0.60  →  Redundant   (Critical)
|ρ| >= 0.35  →  Strong      (High impact)
|ρ| >= 0.25  →  Moderate    (Medium impact)
|ρ| >= 0.15  →  Weak        (Low impact)
|ρ| <  0.15  →  Not reported
```

Where `|ρ|` is the absolute value of the correlation coefficient.

## Negative Correlations

The model supports negative correlations (though current heuristics produce only positive values in v1):

- **Negative ρ**: Indicates mutually exclusive or contradictory outcomes
- **Classification**: Based on |ρ| but tagged as "contradiction" instead of "redundancy"
- **Example** (hypothetical): "Home Win" + "Away Win" would have ρ ≈ -1.0

## Effective Legs Calculation

### Formula

```
N_eff = N / (1 + α * ρ⁺_mean * (N - 1))
```

Where:
- **N**: Number of selections
- **α**: Adjustment factor (default 1.0, configurable via `correlationAlpha`)
- **ρ⁺_mean**: Mean of positive correlations only
- **N_eff**: Effective number of independent legs

### Correlation-Adjusted Probability

```
P_corr = P_naive^(N / N_eff)
```

Where:
- **P_naive**: Product of individual probabilities (naive independence)
- **P_corr**: Correlation-adjusted combined probability

### Example

3 selections with probabilities [0.5, 0.6, 0.7]:
- **P_naive** = 0.5 × 0.6 × 0.7 = 0.21
- If correlations = [0.3, 0.3] (moderate)
- **ρ⁺_mean** = 0.3
- **N_eff** = 3 / (1 + 1.0 × 0.3 × 2) = 3 / 1.6 = 1.875
- **Exponent** = 3 / 1.875 = 1.6
- **P_corr** = 0.21^1.6 ≈ 0.095

Result: Correlation reduces true probability from 21% to ~9.5%.

## Implementation Details

### Location

`backend/correlation/engine.py`

### Key Functions

- `detect_correlations(selections)`: Main entry point
- `_same_match_correlation(s1, s2)`: Same fixture rules
- `_same_team_correlation(s1, s2)`: Cross-match team exposure
- `_same_league_correlation(s1, s2)`: League-wide patterns
- `compute_effective_legs(n, correlations, alpha)`: Effective-legs calculation
- `_classify_correlation(rho)`: Threshold-based classification

### Market Normalization

Markets are normalized to standard types:
- "1x2", "match winner", "match_result" → `"1x2"`
- "over/under", "total", "over_under" → `"totals"`
- "asian", "handicap" → `"handicap"`
- "both teams", "btts" → `"btts"`

## Limitations

### What This Model Does NOT Do

1. **Machine Learning**: No ML; purely heuristic rules
2. **Historical Data**: Does not learn from past match results
3. **Team-Specific**: No team-specific correlation patterns
4. **Market Depth**: Limited to major market types
5. **Dynamic Adjustment**: Coefficients are fixed, not adaptive
6. **Three-Way Correlations**: Only pairwise; no higher-order interactions

### Known Approximations

- Correlation coefficients are **expert-estimated**, not empirically derived
- Same-match correlations ignore specific outcomes (e.g., "Home Win" + "Over" might differ from "Draw" + "Over")
- Time window for same-team exposure is a rough heuristic
- League-wide patterns are oversimplified

### When to Use Caution

- **High N_eff reduction**: If N_eff << N, correlation adjustment is aggressive
- **Redundant selections**: Always remove duplicates rather than rely on correlation adjustment
- **Exotic markets**: Model is calibrated for standard 1X2, totals, BTTS, handicaps

## Assumptions

1. **Correlation linearity**: Assumes linear combination is reasonable
2. **Independence of errors**: Model errors are independent across selections
3. **Positive correlations dominate**: Negative correlations are rare in typical accumulators
4. **Stationary correlations**: Coefficients don't change with time or context

## Future Improvements (Not Implemented)

This documentation describes what IS implemented. Future versions may include:

- **Empirical calibration**: Derive coefficients from historical match data
- **Team-specific correlations**: Model team form and style dependencies
- **Outcome-aware correlations**: Different ρ for "Home Win + Over" vs "Draw + Over"
- **Machine learning**: Use ML to predict correlations from features
- **Time-varying correlations**: Adjust for time-of-season effects

## Validation

### Tests

See `backend/tests/test_correlation_engine.py`:
- Canonical correlation rule tests (1X2↔Totals, BTTS↔Over, etc.)
- Effective legs calculation
- Classification thresholds
- Pairwise detection

### Expected Behavior

- **Zero correlations** → N_eff = N, P_corr = P_naive
- **High correlations** → N_eff < N, P_corr < P_naive (probability decreases)
- **Redundant selections** → Flagged as critical warning

## References

- Effective-legs method adapted from portfolio theory (correlation-adjusted variance)
- Correlation coefficients based on expert judgment and football betting literature

## Disclaimer

**Correlation estimates are approximations**. Real-world correlations vary by team, league, market conditions, and time. This model provides a reasonable starting point but should not be treated as precise.

Use this tool for **educational analysis only**, not as a guarantee of outcomes.
