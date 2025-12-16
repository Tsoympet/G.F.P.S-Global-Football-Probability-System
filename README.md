

**G.F.P.S – Global Football Probability System** is an advanced AI-driven football probability and analytics platform.

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
