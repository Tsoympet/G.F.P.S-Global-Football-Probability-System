
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

- Use a proper database (PostgreSQL) instead of SQLite.
- Configure:
  - `SECRET_KEY`
  - `APIFOOTBALL_KEY`
  - `GOOGLE_CLIENT_ID`
  - `SMTP_*` if email alerts are needed
  - `FCM_SERVER_KEY` if push notifications are used
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

## 6. Mobile Builds

- Android build via Expo EAS or classic `expo build:android`.
- iOS build via EAS.
- Configure app name, slug and icons in `mobile/app.json`.

Once production backend is up (with HTTPS), set:

```bash
EXPO_PUBLIC_API_BASE=https://your-domain.com/api
