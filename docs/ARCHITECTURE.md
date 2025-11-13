

# G.F.P.S – Global Football Probability System
## Architecture Overview

GFPS is composed of three main layers:

1. **Backend (FastAPI, Python)**
2. **Mobile App (React Native / Expo)**
3. **Infrastructure (Docker, nginx, monitoring)**

---

## 1. Backend

**Tech stack:**

- Python 3.x
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite (configurable)
- httpx (external APIs)
- JWT-based auth
- Optional SMTP + FCM (email & push)

### Core Modules

- `models.py` – SQLAlchemy models
  - `User`, `Device`, `AlertRule`, `AlertEvent`
  - `Coupon`, `CouponSelection`
  - `FavoriteLeague`, `FavoriteTeam`
  - `ChatRoom`, `ChatMessage`
  - `TeamStats`
- `auth_utils.py` – password hashing, token creation, token decoding
- `fixtures_api.py` – fixtures listing (via API-Football)
- `coupon_api.py` – coupon creation, listing, details
- `favorites_api.py` – favorite leagues and teams
- `device_api.py` – device registration for push notifications
- `alert_engine.py` – background task:
  - polls live fixtures and odds
  - calls prediction engine
  - triggers alerts and logs events
- `prediction_engine.py` – Poisson-based probability engine:
  - 1X2, Over/Under, GG/NG, generic fallback from odds
- `chat_api.py` & `chat_ws.py` – REST + WebSocket chat
- `stats_api.py` & `stats_context.py` – team statistics and Poisson context

---

## 2. Mobile App (Expo)

**Tech stack:**

- React Native
- Expo Router
- TypeScript
- AsyncStorage

### Main Screens (under `mobile/app/`)

- `index.tsx` – dashboard
- `login.tsx` – Google Sign-In and auth integration
- `fixtures.tsx` – fixtures listing
- `match.tsx` – markets + “add to coupon”
- `coupon.tsx` – current coupon builder
- `coupon-history.tsx` – saved coupons
- `favorites.tsx` – favorite leagues
- `profile.tsx` – account, logout and basic settings
- `community.tsx` – chat overview / rooms (future expansion)
- `live.tsx` – live section (streamer integration)
- `settings.tsx` – placeholder for user preferences

### Shared Logic

- `auth/AuthContext.tsx` – stores JWT and profile for the user
- `coupon/CouponContext.tsx` (if separated) – in-memory coupon state
- `notifications/registerPush.ts` – registration for push notifications

---

## 3. Infrastructure

- `infrastructure/docker-compose.yml`
  - Backend container
  - Database
  - nginx reverse proxy
- `infrastructure/nginx.conf`
  - Reverse proxy to backend
  - HTTPS-ready (Let’s Encrypt configuration can be added)
- `infrastructure/prometheus.yml` & `infrastructure/grafana/`
  - Designed for basic metrics, dashboards and health checks

---

## Data Flow (High Level)

1. **User → Mobile App**
   - selects league, fixture, market
   - adds outcomes to coupon
   - authenticates via Google or email

2. **Mobile App → Backend**
   - requests fixtures & markets (`/fixtures`, `/fixtures/markets`)
   - sends coupon data (`/coupon/create`)
   - manages favorites, alerts, profile

3. **Backend → External APIs**
   - requests fixtures & odds from services like API-Football

4. **Background Engines**
   - `alert_engine` periodically fetches live data
   - uses `prediction_engine` to compute probabilities and EV
   - stores `AlertEvent`s and triggers email / push

---

## Extensibility

GFPS is designed to be:

- **Pluggable** – swap external data providers (API-Football, others)
- **Modular** – each domain (alerts, chat, coupons, stats) is separate
- **Scalable** – multiple backend instances behind nginx & load balancers
- **Extendable** – add new markets, sports, prediction models
