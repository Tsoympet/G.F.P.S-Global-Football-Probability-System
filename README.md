# G.F.P.S – Global Football Probability System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Backend Tests](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/backend-tests.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/frontend-tests.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/frontend-tests.yml)
[![Build](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/build.yml)
[![Docker Build](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/docker-build.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/docker-build.yml)
[![Desktop Installers](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/desktop-release.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/desktop-release.yml)
[![Smoke Tests](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/smoke.yml/badge.svg?branch=main)](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions/workflows/smoke.yml)

**G.F.P.S** is a production-grade football probability and analytics platform.
It blends Poisson/Dixon-Coles modelling, market odds normalization, EV detection, and a modern desktop client to explain match outcomes with transparent math.

> **💰 100% Free Operation:** GFPS runs completely free without any expensive API subscriptions. See the [Free Operation Guide](docs/FREE_OPERATION_GUIDE.md) to get started at **$0/month**.

![GFPS Dashboard](screenshots/01-dashboard.png)

> **📋 Production Readiness:** This repository has undergone a comprehensive security audit and is production-ready. See [docs/AUDIT_REPORT.md](docs/AUDIT_REPORT.md) and the install readiness review in [docs/REPO_READINESS_AUDIT.md](docs/REPO_READINESS_AUDIT.md).

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
- **Advanced Web Scraper**
  - JavaScript rendering support (Playwright) for dynamic sites
  - Multi-page pagination (URL pattern, click, scroll)
  - Automatic selector learning and discovery
  - Proxy support for geo-restricted content
  - Captcha handling hooks
  - HTML structure change detection and alerting
- **Desktop Analytics Suite**
  - Live match center, model monitoring, and EV watchlists
  - WebSocket streaming for fixtures/events/markets
- **Security & Reliability**
  - JWT auth, rate limiting, request validation, structured error handling
  - Snapshot persistence for offline analytics

---

## 📸 Screenshots

Explore the desktop application interface with these screenshots showcasing the main features:

> These captures reflect the current GFPS desktop build (Jan 2026).

### Dashboard
The main dashboard provides an overview of live matches, upcoming fixtures, active models, and EV+ signals.

![Dashboard](screenshots/01-dashboard.png)

### Live Match Center
Monitor live matches with real-time updates and analytics.

![Live Match Center](screenshots/02-live-match-center.png)

> **Updated feed view:** reflects the latest live-tracking layout and odds strip.

### Value Bets (EV+)
Discover value betting opportunities with configurable EV thresholds and advanced filtering options.

![Value Bets](screenshots/03-value-bets.png)

> **New filters:** includes EV band chips and source toggles shown in current build.

### Models & Training
Manage and train prediction models with performance metrics.

![Models & Training](screenshots/04-models-training.png)

> **Model monitor:** current training queue and metrics deck.

### Performance Tracking
Track your betting performance with detailed ROI, hit rate, and drawdown analytics.

![Performance](screenshots/05-performance.png)

> **Performance tiles:** refreshed KPI cards and chart themes.

### Backtest Workbench
Run historical backtests to validate strategies and analyze performance.

![Backtest](screenshots/06-backtest.png)

> **Workbench:** shows the present rules panel and results grid.

### Settings
Configure API endpoints, data providers, themes, and authentication.

![Settings](screenshots/07-settings.png)

> **Settings:** includes provider keys and theme controls from the current build.

---

## 📦 Download & Installation

### Pre-built Installers

Download the latest desktop application installers from the [GitHub Releases page](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/releases):

- **Windows**: Download the `.msi` installer
  - Run the installer and follow the setup wizard
  - Windows may show a SmartScreen warning for unsigned apps - click "More info" → "Run anyway"
  
- **macOS**: Download the `.dmg` file
  - Open the `.dmg` file and drag the app to your Applications folder
  - Right-click the app and select "Open" on first launch to bypass Gatekeeper (for unsigned apps)
  
- **Linux**: Download the `.AppImage` file
  - Make it executable: `chmod +x GFPS*.AppImage`
  - Run it: `./GFPS*.AppImage`

**⚠️ Important:** GFPS Desktop requires a backend API server to function. After installing the desktop app, you'll need to start the backend server. The app will show setup instructions on first launch. See the [First Launch](#first-launch) section below for details.

📖 **For detailed installation instructions, troubleshooting, and system requirements, see [docs/INSTALLERS.md](docs/INSTALLERS.md)**

### First Launch

When you first launch GFPS Desktop after installation:

1. **You will see a "Backend API Not Available" error** - this is expected!
2. **Start the backend server** using one of these methods:
   
   **Option 1: Quick Start Scripts (Easiest)**
   - Download or clone this repository
   - **Windows:** Double-click `start-backend.bat`
   - **macOS/Linux:** Run `./start-backend.sh` in Terminal
   
   **Option 2: Manual Setup**
   ```bash
   # Install Python 3.8+ from python.org
   # Then run:
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   cp .env.example .env
   # Edit .env and set SECRET_KEY (generate with: openssl rand -hex 32)
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify backend is running:** Open http://localhost:8000/health in your browser
4. **The desktop app will automatically connect** and start displaying data—no buttons to press
5. (Optional) **Add your API keys** in **Settings → Data Provider API Keys** to pull live feeds (otherwise seeded data is shown)

📖 **For complete setup instructions, see [docs/INSTALLERS.md](docs/INSTALLERS.md#first-launch)**

### Release Channels

- **Stable releases** (`v1.0.0`, `v0.1.0`): Production-ready builds for all users
- **Beta releases** (`v1.0.0-beta.1`): Experimental builds with new features (may contain bugs)

### Building from Source

If you prefer to build from source or no pre-built installers are available yet, see the [🚀 Getting started locally](#getting-started-locally) section below.

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

> **Note on languages:** The backend is implemented in Python (FastAPI) with a React/Tauri desktop client. The system is not available in C++, and migrating the project to C++ is out of scope for this repository.

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

**📈 Model Performance**: For detailed information about prediction accuracy, performance metrics, and realistic expectations, see [docs/MODEL_ACCURACY.md](docs/MODEL_ACCURACY.md).

---

## ⚠️ Risk Disclaimer

GFPS provides probabilistic analytics, not guarantees. Football outcomes remain uncertain, and nothing in GFPS is financial advice or a promise of profit. Use responsibly and validate against your own risk tolerance.

---

## 🔌 Extensibility

- Swap or add data providers (API-Football, custom feeds, web scraping).
- Extend markets (totals, handicaps, props) and EV filters.
- Add new model components (Elo, xG, ML ensembles).

### Data providers

### 💰 100% Free Data Sources (Recommended)

**GFPS is designed to work completely free of charge!** No expensive APIs required.

The system includes multiple FREE data providers that work seamlessly together:

- **OpenFootball CSV**: ✅ FREE, offline fixtures & results (bundled, no setup needed)
- **Football-Data.org**: ✅ FREE API with generous rate limits (optional free API key)
- **OpenLigaDB**: ✅ FREE German league live scores (no API key needed)
- **Web Scraper**: ✅ FREE scraping from public websites (configurable)

### ⚠️ Premium API (NOT Recommended - Expensive!)

- **API-Football**: ❌ EXPENSIVE subscription (~$50-300/month) - **DISABLED BY DEFAULT**
  - Only needed if you absolutely require live odds data in real-time
  - All core features work perfectly with the free providers above

Enable FREE providers via environment variables:
```bash
ENABLE_FOOTBALL_DATA=1    # Football-Data.org API (FREE)
ENABLE_OPENLIGADB=1       # OpenLigaDB live data (FREE)
ENABLE_API_FOOTBALL=0     # Keep DISABLED - expensive premium API
ENABLE_WEB_SCRAPER=0      # Web scraping from HTML sources (FREE)
ENABLE_LIVE_NETWORK=0     # Allow network requests for scraping
```

See [Web Scraper Documentation](docs/web-scraper.md) for details on configuring HTML scraping.

### Data ingestion pipeline

Run the runnable commands from the repository root:

```bash
python -m backend.pipeline_cli ingest_fixtures   # pull + normalize fixtures/results
python -m backend.pipeline_cli ingest_live       # optional live plug-ins (only if allowed)
python -m backend.pipeline_cli build_features    # build bookmaker-style features
```
- Scale out the pipeline with additional workers and storage backends.

---

## 🚀 Getting started locally

For a cross-platform setup guide (Windows/macOS/Linux), see [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

1. **Install backend dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. **Configure environment**
   - Copy `.env.example` to `.env`
   - For **100% FREE operation** (recommended): Leave `APIFOOTBALL_KEY` empty
   - The system will automatically use FREE data sources (OpenFootball CSV, Football-Data.org, OpenLigaDB)
   - Optional: Add a free Football-Data.org API key from https://www.football-data.org/client/register
   - Optional: Configure SMTP for email alerts, Google OAuth for authentication
3. **Run the FastAPI backend**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Run the desktop app (in another terminal)**
   ```bash
   cd GFPS/desktop
   npm install
   # Optional: Set encryption salt for local storage security
   # Copy .env.example to .env and set VITE_SECRET_SALT=$(openssl rand -hex 32)
   npm run dev
   ```
5. **Create a user and log in**
   - The protected endpoints (`/predictions`, `/odds`, `/value`) require a Bearer token.
   - Sign up via `POST /auth/signup` or use Google OAuth via `POST /auth/google`.
   - Log in from the desktop Settings screen to store the token for subsequent calls.
   - **Pay-per-use model**: Users manage their own API provider subscriptions (API-Football, Football-Data.org, Odds Matrix, etc.).
   - Configure your API keys in the Settings screen under "Data Provider API Keys".
   - The client uses your credentials to fetch data from providers you've subscribed to directly.

The desktop client expects the backend at `http://localhost:8000` by default; adjust `FRONTEND_BASE_URL` if you proxy or deploy elsewhere.

### Desktop client hardening

- Live-connected screens for Dashboard, Match Center (probability/xG curves), Value Scanner, Models, and Settings
- WebSocket streaming with HTTP polling fallback, stale-data indicators, offline toggle, and API health surfacing
- Encrypted local storage for API endpoint, EV threshold, refresh interval, theme, cache TTL, and auth token
- Value Scanner with EV slider, league/market filters, probability floor, CSV export, and threshold-aware API calls
- Cached/offline mode with TTL, manual override, and auto recovery when `/health` comes back online
- Tests: `npm test` (Vitest) and production build: `npm run build`
- Installers: `npm run tauri:build` emits `.msi`, `.dmg`, and `.AppImage` artifacts; CI builds on release tags

---

### 🛠️ CMake helper

If you prefer a simple CMake entry point for automation, the root `CMakeLists.txt` wires Python dependencies and tests:

```bash
cmake -S . -B build
cmake --build build --target install_backend_deps
cmake --build build --target run_backend_tests
```

The `install_backend_deps` target installs into your active Python environment; run these commands inside a virtualenv if you want to avoid mutating system packages.
It pulls from `backend/requirements-dev.txt` (which includes pytest). If you've already prepared an environment, configure with `-DGFPS_SKIP_PIP_INSTALL=ON` to skip the install step when running tests.

---

## 🐳 Run with Docker Compose

If you prefer containers, the `infrastructure/docker-compose.yml` file will start Postgres, the FastAPI backend, and optional observability tools:

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml up --build
```

The backend will listen on port `8000` (or via Nginx on `80` if you keep that service enabled). Update `DATABASE_URL` or streamer flags in `.env` as needed.

### Standalone Docker image

For a single-container backend build, a top-level `Dockerfile` is available:

```bash
docker build -t gfps-backend .
docker run --rm -p 8000:8000 --env-file .env gfps-backend
```

It mirrors the compose backend image and runs `uvicorn main:app` on port `8000`.

---

## 🔎 Quick health check

Use the helper script to verify critical endpoints are reachable:

```bash
AUTH_TOKEN="$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"test@gfps.app","password":"password123"}' http://localhost:8000/auth/signup | jq -r .token)"
AUTH_TOKEN="$AUTH_TOKEN" ./scripts/check_endpoints.sh http://localhost:8000
```

It probes `/health`, `/odds`, `/predictions`, and `/value` and prints a simple OK/failed summary.

---

## 🌱 Key environment variables

> **⚠️ Security Notice:** `SECRET_KEY` is required and must be set before running the application. See [docs/SECURITY.md](docs/SECURITY.md) for production deployment guidelines.

- `SECRET_KEY`: **REQUIRED** - JWT signing key for auth helpers. Generate with `openssl rand -hex 32`.
- `DATABASE_URL`: Database connection string; defaults to SQLite for local use.
- `APIFOOTBALL_KEY`: ⚠️ **NOT RECOMMENDED** - Expensive premium API (~$50-300/month). Leave blank to use FREE data sources.
- `FOOTBALL_DATA_API_KEY`: Optional FREE API key from football-data.org (register at https://www.football-data.org/client/register)
- `ENABLE_FOOTBALL_DATA`: Set to `1` to enable FREE Football-Data.org provider (recommended)
- `ENABLE_OPENLIGADB`: Set to `1` to enable FREE OpenLigaDB provider for German leagues (recommended)
- `ENABLE_API_FOOTBALL`: Keep at `0` - only set to `1` if you have an expensive API-Football subscription
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

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory. See [docs/README.md](docs/README.md) for a complete documentation index.

### Essential Documentation
- [README.md](README.md) - This file, overview and quick start
- [MODEL_ACCURACY.md](docs/MODEL_ACCURACY.md) - **Model accuracy and performance metrics**
- [INSTALLERS.md](docs/INSTALLERS.md) - Desktop installer download and installation guide
- [RELEASE_INSTRUCTIONS.md](RELEASE_INSTRUCTIONS.md) - How to create and publish releases
- [EULA.md](EULA.md) - End User License Agreement for desktop installers
- [LICENSE](LICENSE) - MIT License for the software
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment instructions
- [SECURITY.md](docs/SECURITY.md) - Security best practices and production guidelines
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture and design
- [API_REFERENCE.md](docs/API_REFERENCE.md) - API endpoint specifications

For a complete list of available documentation, see the [Documentation Index](docs/README.md).

---

## 🔒 Security

This repository follows security best practices:
- ✅ No default secrets (SECRET_KEY required)
- ✅ Content Security Policy headers configured
- ✅ Automated security scanning (CodeQL)
- ✅ Input validation and SQL injection protection
- ✅ JWT authentication with token versioning
- ✅ Rate limiting and CORS protection

See [docs/SECURITY.md](docs/SECURITY.md) for detailed security guidelines.
