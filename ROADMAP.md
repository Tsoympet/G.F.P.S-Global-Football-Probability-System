# GFPS Desktop Application Roadmap

This roadmap tracks the FastAPI backend and the React/Tauri desktop client toward a production-grade probability engine with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work.

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
   - **Remaining:** expand beyond match-winner odds, add richer event payloads (cards, corners, substitutions), and persist state for historical queries and replay.

3. **Prediction & EV pipeline** — **partial**
   - A production-grade engine now includes market devigging, team-strength priors, Poisson/Dixon-Coles/Bivariate/Skellam goal models, calibration (Platt/temperature/isotonic/conformal), ensemble pooling, in-play Bayesian updates, and Kelly/edge/EV filters plus evaluation metrics.
   - **Remaining:** wire the engine to real datasets, persist predictions/value bets per snapshot, and schedule recomputation on odds/fixture deltas.

4. **Model lifecycle management** — **partial**
   - `/ml/train`, `/ml/models`, and `/ml/activate/{version}` exist alongside feature schema/builders and baseline classifiers.
   - **Remaining:** implement real training jobs, metric tracking, and a persistent registry/artifact store with activation history.

5. **Authentication, authorization, and settings** — **partial**
   - Auth routes and helpers exist server-side and environment requirements are documented in `.env.example` and `README.md`.
   - **Remaining:** wire desktop login/refresh flows, protect sensitive endpoints, and manage third-party API keys per user/org.

6. **Developer/ops workflow** — **partial**
   - Containerized startup is documented, and `/health` plus `scripts/check_endpoints.sh` provide manual probes; CI smoke tests run on GitHub.
   - **Remaining:** add richer alerts/dashboards, sample data seeds for offline demos, and a one-command dev/compose launcher that brings up backend + desktop with fixtures/odds seeds.

7. **Desktop polish & validation** — **pending**
   - **Remaining:** update desktop calls to use auth where required, add loading/error states against the new endpoints, and validate charts/tables with live or demo data.

## Next up (suggested order)
1) Persist and schedule: store live snapshots, predictions, and value bets; run periodic refresh when odds/fixtures update; and backfill demo seeds for offline use.
2) Broaden live payloads further: add cards/corners/substitutions from upstream, retain recent event history per fixture, and stream them over WebSocket + `/live-odds` payloads.
3) Model lifecycle: swap the simulated trainer for a real dataset-driven job, log metrics to disk/DB, and keep artifacts/activation history.
4) Desktop auth hardening: add refresh/logout UX, guard WebSocket connections, and thread roles/claims through UI navigation.
5) Automation & CI: extend smoke tests to cover desktop API calls, seed demo data into compose images, and publish artifacts from the training job stub.
