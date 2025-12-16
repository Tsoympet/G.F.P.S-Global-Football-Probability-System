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
