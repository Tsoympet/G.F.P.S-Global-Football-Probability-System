# GFPS Desktop Application Roadmap

This roadmap tracks the FastAPI backend and the React/Tauri desktop client toward a production-grade probability engine with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work. The lists under each milestone call out the **specific TODOs** still required for parity with the production brief.

## Current gaps
- **Live data depth:** The streamer pulls API Football live fixtures when configured and the `/ws/live-matches` WebSocket broadcasts odds/markets/events snapshots. Historical retention/queries, richer event types (corners, substitutions), and stronger reconciliation against upstream delays are still thin.
- **Prediction/value robustness:** A full scientific engine now combines market devigging, hierarchical team strength, Poisson/Dixon-Coles variants, in-play Bayesian updates, value staking, and calibration/ensemble layers. Persistence and dataset-driven retraining triggers are still outstanding.
- **Model lifecycle:** ML feature schema, builders, and softmax/GBM baselines exist, but there is no persistent registry, artifact storage, or scheduled retraining.
- **Authentication & desktop wiring:** Login/token storage exists on the desktop and sensitive endpoints require auth. Refresh flows, token invalidation UX, and role-based protection are still missing.
- **Ops & observability:** A smoke-test GitHub Action probes health + core endpoints and a dev script runs backend+desktop locally. Alerts/dashboards and seeded demo data for compose remain open.

## Milestones & tasks
1. **Stabilize API contracts** — **done**
   - FastAPI routers exist for `/predictions`, `/value-bets`, `/ml/train`, `/ml/models`, `/ml/activate/{version}`, `/fixtures`, `/live-odds`, and `/ws/live-matches`, returning shapes the desktop understands.
   - Demo fallbacks are in place when API keys are missing.

2. **Live data ingestion & streaming** — **partial**
   - The `live_streamer` polls API Football when configured and feeds an in-memory live snapshot shared with HTTP/WebSocket consumers.
   - Odds, totals/handicaps, and key events are persisted and broadcast; demo heartbeats run when upstream data is absent.
   - **Remaining TODOs:**
     - Normalize and store additional in-play markets (BTTS, Asian lines, player props) and expose them via WebSocket + `/live-odds`.
     - Ingest and persist richer match events (cards, corners, substitutions, VAR outcomes) and attach recent-history windows per fixture.
     - Add historical retention (DB tables + queries) and optional replay endpoints for QA/backtesting of streaming behavior.

3. **Prediction & EV pipeline** — **partial**
   - A production-grade engine now includes market devigging, team-strength priors, Poisson/Dixon-Coles/Bivariate/Skellam goal models, calibration (Platt/temperature/isotonic/conformal), ensemble pooling, in-play Bayesian updates, and Kelly/edge/EV filters plus evaluation metrics.
   - **Remaining TODOs:**
     - Connect the engine to real historical match/odds datasets; formalize data loaders and validation splits per league.
     - Persist per-snapshot predictions/value bets to the database with versioned model metadata for auditability.
     - Schedule recomputation when odds/fixtures update (Celery/APS) and surface freshness timestamps to clients.

4. **Model lifecycle management** — **partial**
   - `/ml/train`, `/ml/models`, and `/ml/activate/{version}` exist alongside feature schema/builders and baseline classifiers.
   - **Remaining TODOs:**
     - Replace the simulated trainer with real pipelines reading prepared datasets and writing metrics (logloss/Brier/CLV/ROI) to disk/DB.
     - Introduce an artifact store (e.g., local FS/S3-compatible) with signed model binaries and activation history.
     - Add governance hooks: model cards, changelog, rollback handling, and health checks on activation.

5. **Authentication, authorization, and settings** — **partial**
   - Auth routes and helpers exist server-side and environment requirements are documented in `.env.example` and `README.md`.
   - **Remaining TODOs:**
     - Complete desktop login/refresh/logout UX; thread auth headers through WebSocket initiation and all protected calls.
     - Enforce role-based access on sensitive endpoints (model activation, odds ingestion controls, value bet exports).
     - Add secure storage/rotation for third-party API keys per user/org and admin UI to manage them.

6. **Developer/ops workflow** — **partial**
   - Containerized startup is documented, and `/health` plus `scripts/check_endpoints.sh` provide manual probes; CI smoke tests run on GitHub.
   - **Remaining TODOs:**
     - Seed compose images with fixtures/odds/predictions for offline demos and CI determinism.
     - Add monitoring/alerting (uptime, latency, data freshness, model activation success) and dashboards.
     - Provide a single entry-point script/Make target to run backend + desktop + workers with seeded data.

7. **Desktop polish & validation** — **pending**
   - **Remaining TODOs:**
     - Wire auth-aware data fetching for fixtures/odds/predictions/value bets and guard WebSocket reconnect flows.
     - Improve loading/error handling and empty states across match center, value bets, and model diagnostics views.
     - Run end-to-end validation with live/demo payloads to verify charts/tables render the broadened markets and events.

## Next up (suggested order)
1) **Persist and schedule**: finalize DB schemas and workers to store live snapshots, predictions, and value bets; trigger recomputation on odds/fixture deltas; ship demo backfill seeds.
2) **Broaden live payloads**: ingest cards/corners/substitutions/VAR outcomes; expose them in WebSocket + `/live-odds`; retain rolling event history per fixture.
3) **Model lifecycle**: implement real dataset-driven training, persist metrics/artifacts, and record activation/rollback history.
4) **Desktop auth hardening**: finish refresh/logout UX, enforce auth on sockets, and thread roles/claims through navigation + guarded screens.
5) **Automation & CI**: extend smoke tests to desktop-facing calls, seed demo data into compose images, and publish artifacts from training jobs.
