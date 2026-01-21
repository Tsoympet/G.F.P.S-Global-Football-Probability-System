
# GFPS – Deployment Guide

This is a suggested deployment approach using Docker and nginx.

---

## 1. Docker Compose

The `infrastructure/docker-compose.yml` file is designed to run:

- `backend` (FastAPI + Uvicorn)
- `db` (PostgreSQL or similar)
- `nginx` (reverse proxy)

Example (simplified sketch):

- backend:
  - exposes port 8000 internally
  - reads `.env`
- nginx:
  - listens on 80/443
  - proxies `/api` to backend

---

## 2. nginx

`infrastructure/nginx.conf`:

- routes `/api/` to backend service
- serves static files (if any)
- can be extended with Let’s Encrypt certificates:
  - using certbot
  - or via a companion container

---

## 3. Environment

Set environment variables using:

- `.env` file for backend
- Docker secrets or environment injection in compose

---

## 4. Production Checklist

### Required Configuration
- Use a proper database (PostgreSQL) instead of SQLite.
- **REQUIRED**: Set `SECRET_KEY` (generate with `openssl rand -hex 32`)

### Optional Configuration (Based on Your Needs)

**For 100% FREE operation (RECOMMENDED):**
- ✅ Leave `APIFOOTBALL_KEY` empty (uses free data sources)
- ✅ Set `ENABLE_FOOTBALL_DATA=1` (free provider)
- ✅ Set `ENABLE_OPENLIGADB=1` (free provider)
- ⚠️ Set `ENABLE_API_FOOTBALL=0` (avoid expensive subscription)
- See [docs/FREE_OPERATION_GUIDE.md](FREE_OPERATION_GUIDE.md) for details

**For premium features (EXPENSIVE - $50-300/month):**
- ⚠️ `APIFOOTBALL_KEY` - Only if you have an API-Football subscription

**For authentication:**
- `GOOGLE_CLIENT_ID` - If using Google OAuth

**For notifications:**
- `SMTP_*` - If email alerts are needed
- `FCM_SERVER_KEY` - If push notifications are used

### Security & Performance
- Enable HTTPS on nginx.
- Restrict FastAPI debug mode (no `--reload` in production).
- Use a process supervisor or run via uvicorn/gunicorn in production mode.

---

## 5. Monitoring

Use:

- `prometheus.yml` + `grafana/` dashboards as a starting point:
  - backend response times
  - alert engine status
  - error rate
  - DB metrics

---

## 6. Desktop Builds

The desktop client lives in `GFPS/desktop` and is built with Vite + Tauri 2.0.

- Install dependencies: `cd GFPS/desktop && npm install`
- Run locally: `npm run tauri:dev`
- Build release binaries: `npm run tauri:build`
- Signing hooks: set `TAURI_WINDOWS_CERT_THUMBPRINT` or `TAURI_MACOS_IDENTITY` environment variables in CI/your shell to sign installers (kept secret)
- Endpoints consumed: `/predictions`, `/odds`, `/value`, `/health` with polling + cached offline fallback (configurable TTL)
- CI: `.github/workflows/desktop-ci.yml` runs tests/build on PRs; `.github/workflows/desktop-release.yml` ships `.msi`, `.dmg`, `.AppImage` on version tags

Ensure the backend URL is configured in the desktop app's environment before packaging so the client can talk to the API.
