# GFPS – API Reference (High-Level)

This is a high-level overview of the main endpoints. Detailed schemas live in the FastAPI docs (`/docs`).

Base URL (development):

```text
http://localhost:8000
```

## Authentication

GFPS uses a **pay-per-use model** where users are charged only for the external data API providers they consume. There are no subscription tiers or role-based access restrictions.

**OAuth Providers:**
- Google OAuth is fully supported via `POST /auth/google`
- Additional social OAuth providers (Facebook, Twitter, GitHub, etc.) can be easily added following the same pattern

**Endpoints:**
- `POST /auth/signup` – Create a user and return a JWT.
- `POST /auth/login` – Login with email + password (2FA supported).
- `POST /auth/google` – Google OAuth login with ID token.
- `POST /auth/request-reset` – Start password reset flow.
- `POST /auth/confirm-reset` – Confirm password reset token.
- `POST /auth/2fa/setup` – Generate TOTP secret + otpauth URI (Bearer token required).
- `POST /auth/2fa/enable` – Enable 2FA with a TOTP code (Bearer token required).
- `POST /auth/2fa/disable` – Disable 2FA with a TOTP code (Bearer token required).

## Core Data (Bearer token required)

- `GET /fixtures` – Fixture listing (live if API-Football configured; seeded fallback otherwise).
- `GET /live-odds` – Live odds and auxiliary markets.
- `GET /predictions` – Model 1X2 probabilities.
- `GET /value-bets` – EV-ranked value opportunities.
- `GET /pipeline/status` – Snapshot + pipeline health (counts, model version, services).

## Models (Bearer token required)

- `POST /ml/train` – Queue a training run.
- `GET /ml/models` – Model registry and metrics.
- `POST /ml/activate/{version}` – Activate a model version.

## Team Strengths (Bearer token required)

- `POST /stats/team/upsert` – Upsert league/team strength context.
- `GET /stats/team` – Fetch team strength stats.

## Alerts (Bearer token required)

- `POST /alerts/rules` – Create an alert rule.
- `GET /alerts/rules` – List alert rules.
- `PATCH /alerts/rules/{rule_id}` – Update rule details.
- `DELETE /alerts/rules/{rule_id}` – Delete an alert rule.
- `GET /alerts/events` – List alert events.

## Favorites (Bearer token required)

- `POST /favorites/league` – Save a favorite league.
- `GET /favorites/leagues` – List favorite leagues.
- `DELETE /favorites/league/{fav_id}` – Remove a favorite league.
- `POST /favorites/team` – Save a favorite team.
- `GET /favorites/teams` – List favorite teams.
- `DELETE /favorites/team/{fav_id}` – Remove a favorite team.

## Coupons (Bearer token required)

- `POST /coupon/create` – Build a coupon from selections.
- `GET /coupon/list` – List coupons.
- `GET /coupon/{coupon_id}` – Coupon detail.
- `DELETE /coupon/{coupon_id}` – Delete coupon.

## Devices (Bearer token required)

- `POST /devices/register` – Register a device token for notifications.
- `GET /devices` – List registered devices.
- `DELETE /devices/{device_id}` – Remove a device token.

## Health

- `GET /health` – Service + database health.
