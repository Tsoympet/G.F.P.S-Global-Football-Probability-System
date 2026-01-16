# Bet Slip Simulation and Analysis

## Overview

The GFPS Bet Slip is a **SIMULATION and ANALYSIS tool only**. It provides professional-grade accumulator analysis with correlation-aware probability calculations and risk assessment. **This system does NOT execute real bets or handle real money.**

## Purpose

The Bet Slip feature allows users to:

1. Add multiple selections from value bets and predictions
2. Analyze accumulators with correlation-adjusted probabilities
3. Understand the impact of correlations on combined odds and expected value
4. Receive professional analytical reports highlighting risks and opportunities
5. Export analysis for further review

## Architecture

### Frontend (Desktop Client)

**Store**: `GFPS/desktop/src/store/betslip.ts`
- Zustand-based state management
- LocalStorage persistence for slip recovery
- Support for single and accumulator modes

**UI Component**: `GFPS/desktop/src/components/BetSlip.tsx`
- Bottom drawer interface (non-intrusive)
- Clear SIMULATION/ANALYSIS labeling
- Per-selection details and totals
- Analysis report display

**Integration Points**:
- Value Bets screen: "+ Add to Bet Slip" button per row
- Dashboard Top EV table: "+ Add" button per row
- LiveMatchCenter: Optional integration for market outcomes

### Backend (FastAPI)

**Endpoint**: `POST /analysis/betslip`
- Accepts versioned JSON request (schema v1.0)
- Returns comprehensive analysis response

**Processing Pipeline**:
1. Validate odds (decimal > 1.0)
2. Resolve probabilities (use provided or compute via prediction engine)
3. Detect pairwise correlations
4. Compute accumulator totals (naive + correlation-adjusted)
5. Calculate risk metrics
6. Generate professional analysis report

## Data Model

### Selection

```typescript
{
  clientSelectionKey: string;      // Unique identifier
  fixtureId?: string;               // Optional fixture reference
  homeTeam: string;
  awayTeam: string;
  league: string;
  leagueId?: string;
  startTime?: string;               // ISO datetime
  marketType: string;               // "1x2", "totals", "btts", etc.
  marketName: string;
  outcome: string;
  oddsBookmaker: number;            // Decimal odds > 1.0
  oddsFair?: number;                // Computed fair odds
  modelProbability?: number;        // [0, 1]
}
```

### Analysis Request

```json
{
  "schemaVersion": "1.0",
  "slipId": "slip-123456",
  "mode": "accumulator",
  "selections": [...],
  "correlationAlpha": 1.0
}
```

### Analysis Response

Includes:
- Per-selection results (odds, probability, EV, data quality)
- Pairwise correlations with classifications
- Accumulator totals:
  - Combined odds (product)
  - Combined probability (naive + correlation-adjusted)
  - Expected value (naive + correlation-adjusted)
  - Effective legs calculation
  - Risk metrics (score, profile, drivers)
- Professional analysis report (5 sections)

## Persistence

### Desktop LocalStorage

Key: `gfps_betslip`

Stored data:
```json
{
  "selections": [...],
  "mode": "accumulator",
  "savedAt": "2026-01-16T..."
}
```

**Recovery**: Automatically rehydrates on app startup via `hydrate()` action.

**Clearing**: User-controlled "Clear slip" button or `clearSlip()` action.

## User Workflow

1. **Add selections**: Click "+ Add to Bet Slip" on value bets or dashboard
2. **Review selections**: Open bet slip drawer (bottom of screen)
3. **Choose mode**: Single or Accumulator
4. **Analyze**: Click "📊 Analyze Slip" button
5. **Review report**: Executive summary, correlation warnings, scenario analysis, professional notes
6. **Clear or modify**: Remove individual selections or clear entire slip

## Limitations

- **No bet execution**: This is a simulation tool only
- **Correlation detection**: Heuristic-based (v1), not machine learning
- **Probability estimates**: Based on statistical models; not guarantees
- **Market coverage**: Limited to supported market types (1X2, totals, BTTS, handicap)
- **Overround estimation**: Approximate; actual bookmaker margins vary

## Disclaimers

**CRITICAL**: This tool is for educational and informational purposes only. It does NOT constitute financial advice or an encouragement to gamble. All probability calculations are estimates and may not reflect actual outcomes. Gambling involves risk of loss.

**No Guarantees**: Probabilities, correlations, and expected values are statistical estimates. Actual match outcomes are uncertain and may differ significantly from predictions.

**Responsible Use**: Users should only use this tool for analysis and research. Never bet more than you can afford to lose.

## Future Enhancements (Not Implemented)

This documentation describes what IS implemented. Future versions may include:
- Machine learning-based correlation detection
- Historical analysis tracking
- More sophisticated overround calculations
- Additional market types
- Export formats beyond current implementation

## Support

For issues or questions about the Bet Slip feature:
1. Check correlation model documentation: `CORRELATION_MODEL.md`
2. Review analysis engine documentation: `AI_ANALYSIS_ENGINE.md`
3. Consult user guide: `USER_GUIDE_PRO_ANALYSIS.md`
