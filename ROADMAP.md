# GFPS Desktop Application Roadmap

This roadmap focuses on getting the FastAPI backend and the React/Tauri desktop client to run end-to-end with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work.

## Current gaps
- **Live data depth:** The streamer now pulls API Football live fixtures when configured and the `/ws/live-matches` WebSocket broadcasts snapshots. Snapshots, odds, and events are persisted for offline viewing, and totals/handicap lines are exposed, but historical retention/queries and richer event types (corners, substitutions) are still thin.
- **Prediction/value robustness:** Predictions and expected value are derived from implied probabilities and are now persisted/scheduled alongside the live snapshot, but they remain heuristic rather than model-driven.
- **Model lifecycle:** The ML routes now enqueue a training simulation, persist versions/metrics, and support activation, but they are still stubs without real datasets or artifact storage.
- **Authentication & desktop wiring:** Login/token storage now exists on the desktop and sensitive endpoints require auth. Refresh flows, token invalidation UX, and role-based protection are still missing.
- **Ops & observability:** A smoke-test GitHub Action probes health + core endpoints and a dev script runs backend+desktop locally. Alerts/dashboards and seeded demo data for compose remain open.

## Milestones & tasks
1. **Stabilize API contracts** — **done**
   - FastAPI routers now exist for `/predictions`, `/value-bets`, `/ml/train`, `/ml/models`, `/ml/activate/{version}`, `/fixtures`, `/live-odds`, and `/ws/live-matches`, returning shapes the desktop understands.
   - Demo fallbacks are in place when API keys are missing.

2. **Live data ingestion & streaming** — **partial**
   - The `live_streamer` polls API Football when configured and feeds an in-memory live snapshot shared with HTTP/WebSocket consumers.
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
