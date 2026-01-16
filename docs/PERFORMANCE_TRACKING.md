# Performance Tracking

GFPS ships a simulation-only ledger for tracking decisions over time.

## Bet Journal
- Fields: timestamp, fixture IDs, league/team metadata, market/side, model probability, fair odds, bookmaker/closing odds, EV, correlation risk, confidence, stake rule + stake, result (win/loss/push/void), realized ROI.
- Entries are append-only; once settled they cannot be edited. Settlement is automatic when results are ingested, with a `/performance/reconcile` safety valve.
- Supports manual stakes or descriptive stake rules (flat, capped, kelly).

## KPIs
- ROI, yield, hit rate, wins/losses/pushes, EV vs realized ROI
- Drawdown (max + current), variance proxy, CLV proxy (closing vs entry price)
- Breakdowns by league, market, team plus 7/30/90 day windows
- Data quality flags when pending or missing outcomes exist

## Usage
- API: `POST /performance/journal` to log a simulated decision.
- API: `GET /performance/kpis` for KPI cards/curves, auto-reconciles before computing.
- API: `POST /performance/reconcile` to re-check settlement after new results arrive.

Outputs are surfaced in the desktop “Performance” section with KPI cards, drawdown/ROI curves, and breakdown tables plus CSV/JSON export.
