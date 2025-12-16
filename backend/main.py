"""
G.F.P.S – Global Football Probability System
Backend API (FastAPI)

Exposes:
- Auth (local + Google + 2FA + reset)
- Fixtures & markets
- Coupon builder
- Favorites
- Devices (push tokens)
- Stats
- Alerts (rules + events)
- Background engines (alerts + streamer)
"""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models  # noqa: F401  # ensure models are imported

from .google_auth import router as auth_router
from .fixtures_api import router as fixtures_router
from .live_odds_api import router as live_odds_router
from .live_ws import router as live_ws_router
from .markets_api import router as markets_router
from .coupon_api import router as coupon_router
from .favorites_api import router as favorites_router
from .device_api import router as device_router
from .stats_api import router as stats_router
from .alerts_api import router as alerts_router
from .predictions_api import router as predictions_router
from .value_bets_api import router as value_bets_router
from .ml_api import router as ml_router
from .alert_engine import start_alert_engine_background
from .streamer import start_streamer_background
from .fixtures_api import router as fixtures_router
from .live_odds_api import router as live_odds_router
from .live_ws import router as live_ws_router
from .markets_api import router as markets_router
from .coupon_api import router as coupon_router
from .favorites_api import router as favorites_router
from .device_api import router as device_router
from .stats_api import router as stats_router
from .alerts_api import router as alerts_router
from .predictions_api import router as predictions_router
from .value_bets_api import router as value_bets_router
from .ml_api import router as ml_router
from .alert_engine import start_alert_engine_background
from .streamer import start_streamer_background
from .fixtures_api import router as fixtures_router
from .live_odds_api import router as live_odds_router
from .live_ws import router as live_ws_router
from .markets_api import router as markets_router
from .coupon_api import router as coupon_router
from .favorites_api import router as favorites_router
from .device_api import router as device_router
from .stats_api import router as stats_router
from .alerts_api import router as alerts_router
from .predictions_api import router as predictions_router
from .value_bets_api import router as value_bets_router
from .ml_api import router as ml_router
from .alert_engine import start_alert_engine_background
from .streamer import start_streamer_background


app = FastAPI(
    title="GFPS – Global Football Probability System",
    version="0.2.0",
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    # Create all DB tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Start background workers (alerts + live streamer)
    loop = asyncio.get_event_loop()
    start_alert_engine_background(loop)
    start_streamer_background(loop)


# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(fixtures_router)
app.include_router(live_odds_router)
app.include_router(live_ws_router)
app.include_router(predictions_router)
app.include_router(value_bets_router)
app.include_router(ml_router)
app.include_router(markets_router)
app.include_router(coupon_router)
app.include_router(favorites_router)
app.include_router(device_router)
app.include_router(stats_router)
app.include_router(alerts_router)


# -------------------------------------------------------------------
# Health / root
# -------------------------------------------------------------------
@app.get("/")
async def root():
app.include_router(auth_router)
app.include_router(fixtures_router)
app.include_router(live_odds_router)
app.include_router(live_ws_router)
app.include_router(predictions_router)
app.include_router(value_bets_router)
app.include_router(ml_router)
app.include_router(markets_router)
app.include_router(coupon_router)
app.include_router(favorites_router)
app.include_router(device_router)
app.include_router(stats_router)
app.include_router(alerts_router)


# -------------------------------------------------------------------
# Health / root
# -------------------------------------------------------------------
@app.get("/")
async def root():
app.include_router(auth_router)
app.include_router(fixtures_router)
app.include_router(live_odds_router)
app.include_router(live_ws_router)
app.include_router(predictions_router)
app.include_router(value_bets_router)
app.include_router(ml_router)
app.include_router(markets_router)
app.include_router(coupon_router)
app.include_router(favorites_router)
app.include_router(device_router)
app.include_router(stats_router)
app.include_router(alerts_router)


# -------------------------------------------------------------------
# Health / root
# -------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "ok": True,
        "name": "GFPS – Global Football Probability System",
        "version": "0.2.0",
        "status": "running",
    }
