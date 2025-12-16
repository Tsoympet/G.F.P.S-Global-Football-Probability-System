

**G.F.P.S – Global Football Probability System** is an advanced AI-driven football probability and analytics platform.

It combines statistical modelling, live odds data, EV (Expected Value) calculations, and a modern desktop app to help users understand the *true* probability behind football matches and markets.
It combines statistical modelling, live odds data, EV (Expected Value) calculations, and a modern desktop app to help users understand the *true* probability behind football matches and markets.

GFPS doesn’t guess – it calculates.
It doesn’t “tip” – it justifies every suggestion with numbers.

---

## ✨ Key Features

- **Real-Time Probability Engine**
  - 1X2, Over/Under, GG/NG, Asian Lines and more
  - Poisson-based models, league and team strength factors

- **Expected Value (EV) & Value Detection**
  - EV-based filtering of odds
  - Automatic spotting of overpriced/undervalued outcomes

- **Live Streamer & Alerts**
  - WebSocket-based live odds and events ingestion (design-ready)
  - User-defined alert rules (EV thresholds, market swings, team triggers)
  - Email / Push / In-app notifications (integration ready)

- **AI-Powered Coupon Builder**
  - Build tickets from fixtures + markets
  - Combined odds, probability and EV estimation
  - Coupon history and account-linked storage

- **User Accounts & Security**
  - JWT-based auth
  - Optional 2FA
  - Google Sign-In

- **Personalization**
  - Favorite leagues and teams
  - Per-user rules and alerts
  - Saved coupons

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
- **Personalization**
  - Favorite leagues and teams
  - Per-user rules and alerts
  - Saved coupons

- **Community & Collaboration**
  - Real-time chat (rooms per league/match)

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

## 🚀 Getting started locally

1. **Install backend dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. **Configure environment**
   - Copy `.env.example` to `.env` and fill in the values you have (API Football key, SMTP, Google client ID).
   - Leave `APIFOOTBALL_KEY` empty to run with demo fixtures/odds; set `STREAMER_ENABLED=true` only when an API key is present.
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
   - The protected endpoints (fixtures, live odds, predictions, value bets) now require a Bearer token.
   - Sign up via `POST /auth/signup` or log in from the desktop Settings screen to store the token for subsequent calls.

The desktop client expects the backend at `http://localhost:8000` by default; adjust `FRONTEND_BASE_URL` if you proxy or deploy elsewhere.

## 🐳 Run with Docker Compose

If you prefer containers, the `infrastructure/docker-compose.yml` file will start Postgres, the FastAPI backend, and optional observability tools:

```bash
cp .env.example .env   # fill in what you have; defaults fall back to demo data
docker compose -f infrastructure/docker-compose.yml up --build
```

The backend will listen on port `8000` (or via Nginx on `80` if you keep that service enabled). Update `DATABASE_URL` or streamer flags in `.env` as needed.

## 🔎 Quick health check

Use the helper script to verify critical endpoints are reachable:

```bash
AUTH_TOKEN="$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"test@gfps.app","password":"password"}' http://localhost:8000/auth/signup | jq -r .token)"
AUTH_TOKEN="$AUTH_TOKEN" ./scripts/check_endpoints.sh http://localhost:8000
```

It probes `/health`, `/fixtures`, `/live-odds`, `/predictions`, and `/value-bets` and prints a simple OK/failed summary.

## 🛠️ One-command dev stack

Use `./scripts/dev_stack.sh` to boot the backend (uvicorn) and desktop (`npm run dev`) together on ports 8000 and 1420 respectively. Ctrl+C will shut down the backend when you exit the desktop dev server.

## 🌱 Key environment variables
- `SECRET_KEY`: JWT signing key for auth helpers.
- `DATABASE_URL`: Database connection string; defaults to SQLite for local use.
- `APIFOOTBALL_KEY`: Optional API key for live scores/odds. Leave blank to use demo data.
- `STREAMER_ENABLED` / `STREAMER_INTERVAL_SEC`: Enable and tune the live poller; keep disabled without an API key.
- `SNAPSHOT_INTERVAL_SEC`: How often to persist live snapshots + predictions/EV when running the scheduler.
- `ALERT_ENGINE` / `ALERT_ENGINE_INTERVAL_SEC`: Toggle the background alert worker.
- `SMTP_*` / `FCM_SERVER_KEY`: Email/FCM notification credentials (optional).
- `GOOGLE_CLIENT_ID`: Enable Google sign-in flows in the auth helpers.
