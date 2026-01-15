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
