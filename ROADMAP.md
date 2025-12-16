# GFPS Desktop Application Roadmap

This roadmap tracks the FastAPI backend and the React/Tauri desktop client toward a production-grade probability engine with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work. The lists under each milestone call out the **specific TODOs** still required for parity with the production brief.

## Current gaps
- **Live data depth:** The streamer pulls API Football live fixtures when configured and the `/ws/live-matches` WebSocket broadcasts odds/markets/events snapshots. Historical retention/queries, richer event types (corners, substitutions), and stronger reconciliation against upstream delays are still thin.
- **Prediction/value robustness:** A full scientific engine now combines market devigging, hierarchical team strength, Poisson/Dixon-Coles variants, in-play Bayesian updates, value staking, and calibration/ensemble layers. Persistence and dataset-driven retraining triggers are still outstanding.
- **Model lifecycle:** ML feature schema, builders, and softmax/GBM baselines exist, but there is no persistent registry, artifact storage, or scheduled retraining.
- **Authentication & desktop wiring:** Login/token storage exists on the desktop and sensitive endpoints require auth. Refresh flows, token invalidation UX, and role-based protection are still missing.
This roadmap focuses on getting the FastAPI backend and the React/Tauri desktop client to run end-to-end with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work.

## Current gaps
- **Live data depth:** The streamer now pulls API Football live fixtures when configured and the `/ws/live-matches` WebSocket broadcasts snapshots. Snapshots, odds, and events are persisted for offline viewing, and totals/handicap lines are exposed, but historical retention/queries and richer event types (corners, substitutions) are still thin.
- **Prediction/value robustness:** Predictions and expected value are derived from implied probabilities and are now persisted/scheduled alongside the live snapshot, but they remain heuristic rather than model-driven.
- **Model lifecycle:** The ML routes now enqueue a training simulation, persist versions/metrics, and support activation, but they are still stubs without real datasets or artifact storage.
- **Authentication & desktop wiring:** Login/token storage now exists on the desktop and sensitive endpoints require auth. Refresh flows, token invalidation UX, and role-based protection are still missing.
- **Ops & observability:** A smoke-test GitHub Action probes health + core endpoints and a dev script runs backend+desktop locally. Alerts/dashboards and seeded demo data for compose remain open.

## Milestones & tasks
1. **Stabilize API contracts** — **done**
   - FastAPI routers exist for `/predictions`, `/value-bets`, `/ml/train`, `/ml/models`, `/ml/activate/{version}`, `/fixtures`, `/live-odds`, and `/ws/live-matches`, returning shapes the desktop understands.
   - FastAPI routers now exist for `/predictions`, `/value-bets`, `/ml/train`, `/ml/models`, `/ml/activate/{version}`, `/fixtures`, `/live-odds`, and `/ws/live-matches`, returning shapes the desktop understands.
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
   - A `/ws/live-matches` WebSocket broadcasts fixtures plus odds snapshots and supports demo heartbeats when upstream data is absent.
   - **Remaining:** expand beyond match-winner odds, add richer event payloads, and persist state for historical queries.

3. **Prediction & EV pipeline** — **partial**
   - A shared prediction engine derives probabilities from implied odds and produces `Prediction` and `ValueBet` rows in memory.
   - **Remaining:** plug in real models, persist outputs, and recompute when odds/fixtures change instead of on-demand only.

4. **Model lifecycle management** — **partial**
   - `/ml/train`, `/ml/models`, and `/ml/activate/{version}` return demo data and toggle active versions in memory.
   - **Remaining:** implement real training jobs, metric tracking, and a persistent registry/artifact store.

5. **Authentication, authorization, and settings** — **partial**
   - Auth routes and helpers exist server-side and environment requirements are documented in `.env.example` and `README.md`.
   - **Remaining:** wire desktop login/refresh flows, protect sensitive endpoints, and manage third-party API keys per user/org.

6. **Developer/ops workflow** — **partial**
   - Containerized startup is documented, and `/health` plus `scripts/check_endpoints.sh` provide manual probes.
   - **Remaining:** add CI smoke tests, sample data seeds for offline demos, and a one-command dev/compose launcher that brings up backend + desktop.

7. **Desktop polish & validation** — **pending**
   - **Remaining:** update desktop calls to use auth where required, add loading/error states against the new endpoints, and validate charts/tables with live or demo data.

## Next up (suggested order)
1) Persist and schedule: store live snapshots, predictions, and value bets; run periodic refresh when odds/fixtures update; and backfill demo seeds for offline use.
2) Broaden live payloads further: add cards/corners/substitutions from upstream, retain recent event history per fixture, and stream them over WebSocket + `/live-odds` payloads.
3) Model lifecycle: swap the simulated trainer for a real dataset-driven job, log metrics to disk/DB, and keep artifacts/activation history.
4) Desktop auth hardening: add refresh/logout UX, guard WebSocket connections, and thread roles/claims through UI navigation.
5) Automation & CI: extend smoke tests to cover desktop API calls, seed demo data into compose images, and publish artifacts from the training job stub.
This roadmap focuses on getting the FastAPI backend and the React/Tauri desktop client to run end-to-end with live data, model outputs, and alerting.

## Current gaps
- **Backend endpoints vs. desktop expectations:** The desktop app requests `/predictions`, `/value-bets`, and `/ml/*` routes (see `GFPS/desktop/src/api/client.ts`), but the backend only exposes fixtures, live odds, markets, and some alert/device endpoints. Predictions, value bets, and model management must be implemented and wired into FastAPI.
- **Live data transport:** The desktop client opens a WebSocket at `/ws/live-matches` via `useLiveMatches` (see `GFPS/desktop/src/hooks/useLiveMatches.ts`), but the backend has no WebSocket route or publisher. The `backend/streamer` loop is also a stub and does not ingest live scores/odds or emit events.
- **EV/value workflow:** The desktop UI expects `ValueBet` rows (see `GFPS/desktop/src/screens/ValueBets.tsx`), but the backend’s `value_api.py` exposes a different path/shape (`/value-picks` with DB models). There is no pipeline that computes expected value from live odds and model probabilities.
- **Prediction/model lifecycle:** There is no `/predictions` API, no persisted predictions, and no model registry surfaced to the desktop. `ModelsTraining.tsx` calls `/ml/train`, `/ml/models`, and `/ml/activate/{version}`, none of which exist server-side.
- **Authentication & settings:** JWT/Google auth helpers exist but the desktop has no auth wiring. Environment setup (API keys, DB URL, streamer flags) is undocumented for developers.
- **Packaging & ops:** There are Docker/infrastructure stubs but no compose/dev workflow that runs backend + desktop together with seeded data.

## Milestones & tasks
1. **Stabilize API contracts**
   - Add FastAPI routers for `/predictions`, `/value-bets`, `/ml/train`, `/ml/models`, and `/ml/activate/{version}` that return the shapes expected by the desktop types.
   - Align existing routes (`/fixtures`, `/live-odds`, `/fixtures/markets`) with desktop field names and add error handling/logging.

2. **Live data ingestion & streaming**
   - Implement the `backend/streamer/live_streamer.py` loop to pull scores/odds from API Football (or another provider) and normalize them.
   - Add a WebSocket endpoint `/ws/live-matches` that broadcasts fixture snapshots and match events consumed by `useLiveMatches`.
   - Introduce an in-memory cache or DB tables to track live fixtures, events, and odds for both HTTP and WebSocket consumers.

3. **Prediction & EV pipeline**
   - Build a prediction service that scores fixtures (pre-match and in-play) and stores probabilities with fixture IDs.
   - Create an EV calculator that joins model probabilities with live/book odds to produce `ValueBet` rows and exposes them through the new `/value-bets` endpoint.
   - Schedule periodic recomputation or trigger recalculation when new odds arrive.

4. **Model lifecycle management**
   - Implement `/ml/train` to kick off training jobs (initially synchronous/dummy, then background tasks) and persist versioned metrics.
   - Expose `/ml/models` with model metadata (version, ROI, logloss, status) and `/ml/activate/{version}` to mark the active model.
   - Persist model registry information (DB or filesystem) and load the active model in the prediction service.

5. **Authentication, authorization, and settings**
   - Decide on auth flow for the desktop (JWT login or Google sign-in) and expose the necessary routes/UI wiring.
   - Secure value/prediction endpoints where appropriate and handle API key management for third-party feeds.
   - Document required environment variables (API keys, DB URL, streamer flags) and provide `.env.example`.

6. **Developer/ops workflow**
   - Add Docker Compose or a `make dev` script to start backend, database, and desktop in one command with demo data.
   - Seed sample fixtures/odds/predictions for offline demos when API keys are absent.
   - Add automated tests or health checks for critical endpoints (fixtures, live odds, predictions, value bets).

7. **Desktop polish & validation**
   - Hook UI components to the new endpoints and handle loading/error states.
   - Verify charts/tables render with real data; add placeholder states where data is unavailable.
   - Package the Tauri app with an updated backend URL configuration for staging/production.

## Next up (suggested order)
1) Ship minimal server implementations for `/predictions`, `/value-bets`, and `/ml/models` that return hard-coded/demo data matching the desktop types.
2) Add a lightweight `/ws/live-matches` WebSocket that reuses existing fixture demo data and emits a heartbeat, then expand with real streamer integration.
3) Document environment and runbooks (API keys, how to start backend + desktop) to unblock contributors before tackling full EV/prediction pipelines.
