# Metrics Glossary

- **ROI**: Profit / Total Stake. Uses realized results only.
- **Yield**: Profit / Number of bets.
- **Hit Rate**: Wins / Settled bets.
- **EV**: `(model_probability * odds) - 1`.
- **Realized ROI**: Actual return per bet using settlement result.
- **CLV Proxy**: Avg. `(closing_odds - entry_odds) / entry_odds` for settled bets.
- **Drawdown**: Peak equity minus current equity over time.
- **Variance Proxy**: Population variance of per-bet PnL.
- **Correlation Risk**: Simple flag when multiple picks target the same fixture.
- **Data Quality Flag**: Count of pending or missing settlements.
- **Honesty Panel**: Sample-size and completeness warnings shown on backtests.
