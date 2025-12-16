# GFPS Desktop Application Roadmap

This roadmap focuses on getting the FastAPI backend and the React/Tauri desktop client to run end-to-end with live data, model outputs, and alerting. Items marked as **done** have shipped; remaining bullets describe the next slices of work.

## Current gaps
- **Live data depth:** The streamer now pulls API Football live fixtures when configured and the `/ws/live-matches` WebSocket broadcasts snapshots, but there is no persistence of historical events, and the payloads are limited to a single market (1X2) with basic score/time fields. Odds for other markets and richer match events (cards, corners) are not streamed.
- **Prediction/value robustness:** Predictions and expected value are derived from implied probabilities of the latest odds; there is no trained model, persistence layer, or scheduling to refresh outputs. Value bets are recomputed in memory and not stored.
- **Model lifecycle:** Demo endpoints for `/ml/train`, `/ml/models`, and `/ml/activate/{version}` exist but do not run real training jobs or record metrics/versions. There is no registry or artifact storage.
- **Authentication & desktop wiring:** Auth routes exist server-side, but the desktop client still bypasses login and assumes open endpoints. Token storage/refresh and protected routes remain to be wired on the frontend.
- **Ops & observability:** A basic `/health` route and sample `check_endpoints.sh` script exist, but there are no automated smoke tests, alerts, or dashboards. Containerized workflows are documented, yet there is no CI pipeline or seeded demo DB for compose-based runs.

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
2) Broaden live payloads: add additional markets (totals, handicaps), key events (cards, corners, substitutions), and include them in WebSocket and HTTP responses.
3) Model lifecycle: replace demo `/ml/train` with a real training job skeleton, emit metrics, and persist model versions/activation state.
4) Desktop auth wiring: add login/token handling in the client and secure the backend endpoints that should require authentication.
5) Automation & CI: create compose/dev scripts to run backend + desktop together, add CI smoke tests hitting `/health`, `/fixtures`, `/live-odds`, `/predictions`, and `/value-bets`.
