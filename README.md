**G.F.P.S – Global Football Probability System** is a production-grade football probability and analytics platform.
It blends Poisson/Dixon-Coles modelling, market odds normalization, EV detection, and a modern desktop client to explain match outcomes with transparent math.

---

## ✨ Key Features

- **Probability Engine**
  - 1X2, totals, and BTTS probabilities from Poisson + Dixon-Coles
  - League and team-strength adjustments with recent form weighting
  - Market-derived calibration via overround/shin de-vigging
- **Expected Value (EV) Engine**
  - EV = (prob * odds) - 1 with configurable thresholds
  - Value bet surfacing in the dashboard and alert engine
- **Live Odds & Alerts**
  - Live odds ingestion with validation + market normalization
  - Alert rules by league, market, odds bands, and EV thresholds
- **Desktop Analytics Suite**
  - Live match center, model monitoring, and EV watchlists
  - WebSocket streaming for fixtures/events/markets
- **Security & Reliability**
  - JWT auth, rate limiting, request validation, structured error handling
  - Snapshot persistence for offline analytics

---

## 🧱 Repository Structure

```text
GFPS/desktop/    # React + Tauri desktop client
backend/          # FastAPI backend, models, alert engine, prediction engine
infrastructure/   # Docker, nginx, monitoring configs
docs/             # Architecture & API documentation
scripts/          # Helper scripts (DB init, seeding, etc.)
branding/         # Logo prompts, brand guidelines
```

---

## 🧠 Architecture Overview

GFPS runs a live analytics pipeline that streams fixtures/odds, computes probabilities, and persists snapshots for offline review.

1. **Ingestion** – API-Football pulls fixtures, events, and odds (seeded fallback data if no key).
2. **Normalization** – Odds are de-vigged, markets validated, and fixtures sanitized.
3. **Prediction Engine** – Poisson + Dixon-Coles with team-strength/form adjustments, market pooling, and calibration.
4. **EV Engine** – EV = (prob × odds) − 1 with threshold filtering for value bets.
5. **Persistence & Delivery** – Snapshots, predictions, and EV lists are stored and served to the desktop client.

---

## 📊 Model & EV Engine

- **Goal model**: Poisson goals with Dixon-Coles low-score correction.
- **Team strength**: league/team attack & defense multipliers + recent form weighting.
- **Market calibration**: overround + Shin de-vigging blended with model outputs using linear pooling.
- **Probability calibration**: temperature scaling to keep distributions coherent and well-calibrated.
- **Expected value**: `EV = (prob × odds) − 1`, filtered via `EV_MIN_THRESHOLD`.

---

## ⚠️ Risk Disclaimer

GFPS provides probabilistic analytics, not guarantees. Football outcomes remain uncertain, and nothing in GFPS is financial advice or a promise of profit. Use responsibly and validate against your own risk tolerance.

---

## 🔌 Extensibility

- Swap or add data providers (API-Football, custom feeds).
- Extend markets (totals, handicaps, props) and EV filters.
- Add new model components (Elo, xG, ML ensembles).
- Scale out the pipeline with additional workers and storage backends.

---

## 🚀 Getting started locally

1. **Install backend dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. **Configure environment**
   - Copy `.env.example` to `.env` and fill in the values you have (API Football key, SMTP, Google client ID).
   - If `APIFOOTBALL_KEY` is empty, GFPS serves seeded fixtures only (no live odds).
3. **Run the FastAPI backend**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Run the desktop app (in another terminal)**
   ```bash
   cd GFPS/desktop
   npm install
   npm run dev
   ```
5. **Create a user and log in**
   - The protected endpoints (fixtures, live odds, predictions, value bets) require a Bearer token.
   - Sign up via `POST /auth/signup` or log in from the desktop Settings screen to store the token for subsequent calls.

The desktop client expects the backend at `http://localhost:8000` by default; adjust `FRONTEND_BASE_URL` if you proxy or deploy elsewhere.

### Desktop client hardening

- Live-connected screens for Dashboard, Match Center, Value Scanner, Models, and Settings
- WebSocket streaming with HTTP polling fallback, stale-data indicators, and API health surfacing
- Encrypted local storage for API endpoint, EV threshold, refresh interval, theme, and auth token
- Value Scanner with EV slider, league/market filters, EV/kickoff sorting, and threshold-aware API calls
- Tests: `npm test` (Vitest) and production build: `npm run build`
- Installers: `npm run tauri:build` emits `.msi`, `.dmg`, and `.AppImage` artifacts

---

## 🐳 Run with Docker Compose

If you prefer containers, the `infrastructure/docker-compose.yml` file will start Postgres, the FastAPI backend, and optional observability tools:

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml up --build
```

The backend will listen on port `8000` (or via Nginx on `80` if you keep that service enabled). Update `DATABASE_URL` or streamer flags in `.env` as needed.

---

## 🔎 Quick health check

Use the helper script to verify critical endpoints are reachable:

```bash
AUTH_TOKEN="$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"test@gfps.app","password":"password123"}' http://localhost:8000/auth/signup | jq -r .token)"
AUTH_TOKEN="$AUTH_TOKEN" ./scripts/check_endpoints.sh http://localhost:8000
```

It probes `/health`, `/fixtures`, `/live-odds`, `/predictions`, and `/value-bets` and prints a simple OK/failed summary.

---

## 🌱 Key environment variables
- `SECRET_KEY`: JWT signing key for auth helpers.
- `DATABASE_URL`: Database connection string; defaults to SQLite for local use.
- `APIFOOTBALL_KEY`: API key for live scores/odds. Leave blank for seeded fixtures only.
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins.
- `RATE_LIMIT_PER_MINUTE`: Request rate limit per client (default 120).
- `MODEL_VERSION`: Label stored with prediction and EV snapshots.
- `EV_MIN_THRESHOLD`: Minimum EV required to surface value bets (default 0.02).
- `DIXON_COLES_RHO`: Dixon-Coles correlation parameter for low-score adjustments.
- `STREAMER_ENABLED` / `STREAMER_INTERVAL_SEC`: Enable and tune the live poller.
- `SNAPSHOT_INTERVAL_SEC`: How often to persist live snapshots + predictions/EV.
- `ALERT_ENGINE` / `ALERT_ENGINE_INTERVAL_SEC`: Toggle the background alert worker.
- `SMTP_*` / `FCM_SERVER_KEY`: Email/FCM notification credentials (optional).
- `GOOGLE_CLIENT_ID`: Enable Google sign-in flows in the auth helpers.
