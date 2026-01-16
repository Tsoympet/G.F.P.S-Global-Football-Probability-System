# GFPS Product Roadmap

This roadmap summarizes what is implemented today and outlines optional future enhancements without interim language.

## Implemented foundations
- Live fixture ingestion + WebSocket broadcast (`/ws/live-matches`) backed by an in-memory snapshot store.
- Odds normalization with validation for match winner markets, totals, and handicaps.
- Probability engine using Poisson + Dixon-Coles, team strengths, and recent form adjustments.
- EV pipeline with configurable thresholds and alerting rules.
- Model lifecycle endpoints (`/ml/train`, `/ml/models`, `/ml/activate/{version}`) with persisted metrics.
- Desktop client wired to predictions, value bets, and live analytics.
- Auth, rate limiting, validation, and structured error handling.

## Optional future enhancements
- Persist richer event feeds (cards, corners, substitutions) and historical replay APIs.
- Add model artifact storage and activation history with rollback support.
- Expand market coverage (player props, Asian lines) with dedicated probability calculators.
- Extend observability with dashboards/alerts for data freshness and model performance.

## Competitive research (Jan 2026)
- [Polymarket-live-odds-trading](https://github.com/pietrobogani/Polymarket-live-odds-trading): In-play Poisson/Skellam trading bot; consider a pluggable exchange/execution adapter and latency-aware in-play model updates.
- [Football-Match-Prediction-App](https://github.com/richway-cmd/Football-Match-Prediction-App): Blends ML with odds-derived features; explore an ensemble head alongside Poisson/Dixon-Coles plus Skellam scoreline calibration.
- [football-analytics-dashboard](https://github.com/itzmore-mph/football-analytics-dashboard) and [expected-goals](https://github.com/ChloeGobe/expected-goals): xG modeling with interactive dashboards; add an xG pipeline and lightweight dashboard widgets (shot maps, pass networks) to complement EV outputs.
- [GoalGuru_V1](https://github.com/spectrumkil01-oss/GoalGuru_V1) and [football-odds](https://github.com/tocular/football-odds): Dixon-Coles with value-bet surfacing and GBM ensembles; consider value-scanner presets plus an optional boosting ensemble for calibration.

### Shortlist to implement next
- Backend: add pluggable exchange/execution adapter interface (start with a mock) to support in-play EV-triggered actions; extend in-play model loop to accept faster odds/event deltas.
- Modeling: prototype a GBM/boosting calibration head on top of Poisson/Dixon-Coles outputs and compare vs current temperature scaling.
- xG: build a minimal expected-goals pipeline (feature builder + model stub) and expose summary endpoints; add shot-map/pass-network widgets in the desktop dashboard.
- Value scanner: ship preset filters (leagues/markets/EV bands) inspired by value-bet scanners and allow quick toggles in the desktop UI.
