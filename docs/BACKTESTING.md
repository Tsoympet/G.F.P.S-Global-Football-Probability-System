# Backtesting Workbench

The backtest engine replays historical snapshots and applies “follow GFPS advice” rules without look-ahead.

## Inputs
- Historical fixtures + results
- Prediction snapshots (probabilities + fair odds)
- Odds snapshots when present (falls back to fair odds)

## Rules
- Market filter (1X2-focused in this release)
- EV threshold, confidence threshold
- Max selections per day
- League/team filters
- Correlation filter to avoid stacking the same fixture
- Stake model: flat or fractional Kelly with optional cap

## Outputs
- ROI, yield, hit rate, profit/stake totals
- Drawdown curve + distribution of returns
- Performance by league/market
- Correlation impact (filter on/off)
- Sensitivity sweeps over EV thresholds
- Honesty panel: sample size + data completeness warnings

## API
- `POST /performance/backtests` with date range + rules starts a deterministic run (seeded).
- `GET /performance/backtests` or `/{id}` returns stored runs and metrics.

The desktop “Backtest” screen lets you configure rules, run, and download JSON/CSV for further review.
