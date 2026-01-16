# User Guide: Professional Bet Slip Analysis

## Introduction

Welcome to the GFPS Professional Bet Slip Analysis tool. This guide will help you understand how to use the bet slip for accumulator simulation and analysis.

**IMPORTANT**: This is a **SIMULATION and ANALYSIS tool ONLY**. It does NOT execute real bets or handle real money. All features are designed for educational and analytical purposes.

## Getting Started

### Opening the Bet Slip

The bet slip is accessible as a **bottom drawer** on all screens:

1. **When Closed**: Click the bet slip indicator at the bottom-right corner
2. **When Open**: The drawer expands to show your selections and analysis options

### Adding Selections

You can add selections from multiple sources:

#### From Value Bets Screen
1. Navigate to "Value Bets (EV+)" in the sidebar
2. Browse the value bets table
3. Click "+ Add to Bet Slip" button for any selection
4. The selection is added to your slip and the drawer opens

#### From Dashboard
1. View the "Top EV+ Opportunities" section
2. Click "+ Add" button next to any opportunity
3. The selection is added to your slip

### Viewing Your Selections

Once added, each selection displays:
- **Match**: Home team vs Away team
- **Market & Outcome**: e.g., "Match Winner - home"
- **Odds**: Bookmaker's decimal odds
- **Probability**: Model's estimated probability (if available)

You can **remove** individual selections by clicking the ✕ button.

## Choosing Analysis Mode

### Single Mode
- Analyzes each selection independently
- Useful for comparing individual bets
- No correlation adjustments (single bets are independent)

### Accumulator Mode (Default)
- Combines all selections into one accumulator
- Applies correlation detection and adjustment
- Shows combined odds, probability, and EV
- **Recommended** for analyzing multi-leg parlays

Switch modes using the buttons at the top of the slip.

## Running Analysis

1. **Add Selections**: Ensure you have at least one selection in the slip
2. **Choose Mode**: Single or Accumulator
3. **Click "📊 Analyze Slip"**: The system sends your selections to the backend
4. **Wait for Results**: Analysis typically completes in 1-2 seconds
5. **Review Report**: The analysis report appears below your selections

## Understanding the Analysis Report

### Executive Summary

**Key Metrics**:
- **Combined Odds**: Product of all bookmaker odds
- **Risk Profile**: LOW, MEDIUM, or HIGH
  - **Low**: Well-structured accumulator with good probability
  - **Medium**: Moderate risk; some concerns
  - **High**: Fragile accumulator with low win probability or high correlations
- **Probability (naive)**: Assumes selections are independent
- **Probability (adjusted)**: Accounts for correlations between selections
- **EV (naive / adjusted)**: Expected value as ROI percentage
  - **Positive EV**: Suggests potential value
  - **Negative EV**: Indicates unfavorable odds on average

**Key Insight**: One-line summary of the accumulator's characteristics

### Effective Legs

If selections are correlated, the analysis shows:
- **Effective legs**: Adjusted count (e.g., 2.5 / 3)
- Lower effective legs = higher correlation impact
- Effective legs < actual legs indicates correlation reduces true probability

### Correlation Warnings

The system detects correlations between selections:

#### Warning Levels
- **CRITICAL**: Redundant selections (same market/outcome)
  - **Action**: Remove duplicate immediately
- **HIGH**: Strong correlations (e.g., BTTS + Over on same match)
  - **Impact**: Combined probability is significantly overstated
- **MEDIUM**: Moderate correlations
  - **Impact**: Some overestimation of true probability
- **LOW**: Weak correlations
  - **Impact**: Minimal effect on accumulator

#### Correlation Types
- **Redundancy**: Selections move together (positive correlation)
  - Example: "Home Win" + "Asian Handicap Home" on same match
- **Contradiction**: Selections are mutually exclusive or opposing
  - Example: "Home Win" + "Away Win" (hypothetical)

**How to Use**:
- Review critical/high warnings carefully
- Consider removing highly correlated selections
- Understand that naive odds are misleading when correlations are high

### Scenario Analysis

**Win Requirement**:
- Explains that ALL selections must win for accumulator to pay out
- Shows correlation-adjusted probability vs naive

**Failure Points**:
- **Weakest Link**: Selection with lowest win probability
  - This is your primary risk
- **Multi-leg Fragility** (3+ legs): Probability at least one selection loses
  - Shows how multiple legs compound failure risk

**How to Use**:
- Identify and review the weakest selection
- Assess if the accumulator is too fragile (many legs, low probabilities)

### Professional Notes

Analytical observations about your slip:

#### Categories
- **Market Efficiency**: Comments on odds pricing and value
- **Timing**: Time-sensitive considerations (e.g., odds shifts near kickoff)
- **Trap**: Warnings about common pitfalls
- **Opportunity**: Potential value or market inefficiencies

**Example Notes**:
- "High correlation creates EV illusion; naive calculation is misleading"
- "Odds may shift as fixtures approach"
- "Positive EV suggests potential market inefficiency"

**How to Use**:
- Read all notes carefully
- Pay special attention to "trap" warnings
- Use "opportunity" notes to inform (not dictate) decisions

## Managing Your Slip

### Clear Slip
- Click "Clear" button to remove all selections
- Useful for starting fresh or resetting

### Persistence
- Your slip is automatically saved to browser localStorage
- Selections persist across browser sessions
- Cleared slips are also persisted (empty state)

### Drawer Toggle
- Click the ✕ button to collapse the drawer
- Click the bet slip indicator to reopen
- Drawer state does NOT persist (always starts closed on reload)

## Best Practices

### 1. Avoid Redundant Selections
- Never add the same market/outcome twice
- System will warn you, but prevention is better
- Example: Don't add "Home Win" twice for same match

### 2. Understand Correlations
- Same-match selections are often correlated
- Read correlation warnings carefully
- Adjust your expectations when correlations are detected

### 3. Review Risk Profile
- **High Risk**: Seriously consider simplifying (fewer legs, higher probabilities)
- **Medium Risk**: Acceptable for analysis; understand the trade-offs
- **Low Risk**: Better-structured accumulator

### 4. Focus on Correlation-Adjusted Metrics
- **Ignore naive values** when high correlations are present
- **Use adjusted probability and EV** for decision-making
- Effective legs is your guide to correlation impact

### 5. Use as Educational Tool
- This is NOT a betting recommendation system
- Use to understand probability, correlation, and risk
- Do NOT treat positive EV as a guarantee of profit

## Common Scenarios

### Scenario 1: Same Match, Multiple Markets
**Example**: Team A to win + Over 2.5 goals (same match)

**What Happens**:
- Correlation detected: "1X2 and Over/Under on same match have moderate correlation"
- Adjusted probability < naive probability
- Risk profile may increase

**What to Do**:
- Understand the correlation impact
- Consider if the accumulator adds value vs separate singles

### Scenario 2: High Risk Profile
**Example**: 5-leg accumulator, combined probability = 8%

**What Happens**:
- Risk profile: HIGH
- Scenario: "92% chance of at least one selection failing"
- Professional note: "High number of legs increases volatility"

**What to Do**:
- Question whether 5 legs is necessary
- Consider reducing to 2-3 legs
- Focus on higher-probability selections

### Scenario 3: Negative EV (Adjusted)
**Example**: 3 selections, EV_adjusted = -0.08 (-8%)

**What Happens**:
- Executive summary shows negative EV
- Professional note: "Negative expected value indicates efficient market pricing or unfavorable odds"

**What to Do**:
- Understand that on average, this accumulator loses 8% of stake
- Consider if entertainment value justifies negative EV
- Do NOT expect profit from repeated negative-EV accumulators

## Limitations You Should Know

### 1. Correlation Model is Heuristic
- Based on expert rules, not machine learning
- Coefficients are estimates, not empirical measurements
- May not capture all nuances of real-world correlations

### 2. Probabilities are Estimates
- Model probabilities are statistical projections
- Actual match outcomes are uncertain
- Do NOT treat probabilities as guarantees

### 3. Market Coverage
- Supports major markets: 1X2, Totals, BTTS, Handicap
- Exotic markets may have limited support
- Player props use simplified analysis

### 4. No Real-Time Updates
- Analysis is a snapshot at the time of request
- Odds and probabilities may change before kickoff
- Re-analyze if significant time has passed

### 5. No Historical Tracking (v1)
- This version does not track analysis history
- Each analysis is independent
- Future versions may add history features

## Troubleshooting

### "No selections to analyze"
- **Cause**: Slip is empty
- **Fix**: Add at least one selection before clicking Analyze

### "Failed to analyze bet slip"
- **Cause**: Backend error or network issue
- **Fix**: Check your internet connection; try again in a few seconds

### Analysis shows all zeros
- **Cause**: Invalid probability or odds data
- **Fix**: Remove problematic selections and re-add; report bug if persistent

### Correlation warnings seem wrong
- **Cause**: Heuristic model limitations
- **Note**: Correlation model is v1 and may not be perfect
- **Action**: Use professional judgment; treat as guidance, not absolute truth

## Disclaimer

**CRITICAL REMINDERS**:

1. **No Real Betting**: This tool does NOT execute bets or handle money
2. **Educational Only**: For analysis and learning; not financial advice
3. **No Guarantees**: Probabilities are estimates; outcomes are uncertain
4. **Responsible Use**: Never bet more than you can afford to lose
5. **Seek Help**: If gambling becomes a problem, seek professional support

## FAQ

**Q: Can I export my analysis?**
A: Not in v1. Future versions may add export features.

**Q: How often should I re-analyze?**
A: If odds change significantly or selections are added/removed, re-analyze.

**Q: What if I disagree with the correlation detection?**
A: The model is heuristic and may not be perfect. Use your judgment. Feedback is welcome for future improvements.

**Q: Can I save multiple slips?**
A: Not in v1. Only one slip is persisted at a time.

**Q: Does this work for live betting?**
A: The tool can analyze live odds if you input them, but it's designed for pre-match analysis.

**Q: Why is adjusted EV different from naive EV?**
A: Correlations reduce true combined probability, which affects EV calculation.

## Support and Feedback

For questions, bugs, or feature requests:
1. Consult `BET_SLIP.md` for system architecture
2. Review `CORRELATION_MODEL.md` for correlation details
3. Check `AI_ANALYSIS_ENGINE.md` for report structure
4. Report issues via GitHub or support channels

## Conclusion

The GFPS Bet Slip Analysis tool empowers you to make informed decisions through transparent, correlation-aware accumulator analysis. Use it responsibly, understand its limitations, and remember: **this is for education and analysis, not betting recommendations**.

Happy analyzing! 📊
