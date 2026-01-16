"""
G.F.P.S – Global Football Probability System
Backend API (FastAPI)
"""

import asyncio
import logging
import os
import time
from collections import deque

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler

from .auth_utils import SECRET_KEY
from .db import Base, engine
from . import models  # noqa: F401  # ensure models are imported
from .alert_engine import start_alert_engine_background
from .alerts_api import router as alerts_router
from .analysis_api import router as analysis_router
from .coupon_api import router as coupon_router
from .device_api import router as device_router
from .favorites_api import router as favorites_router
from .fixtures_api import router as fixtures_router
from .google_auth import router as auth_router
from .health_api import router as health_router
from .live_odds_api import router as live_odds_router
from .live_ws import router as live_ws_router
from .markets_api import router as markets_router
from .ml_api import router as ml_router
from .replay_api import router as replay_router
from .predictions_api import router as predictions_router
from .pipeline_api import router as pipeline_router
from .performance_api import router as performance_router
from .snapshot_service import backfill_seed_if_empty, start_snapshot_scheduler
from .odds_snapshot_pipeline import start_odds_snapshot_scheduler
from .stats_api import router as stats_router
from .streamer import start_streamer_background
from .value_bets_api import router as value_bets_router
from .observability_api import router as observability_router
from .xg_api import router as xg_router

app = FastAPI(
    title="GFPS – Global Football Probability System",
    version="0.2.0",
)

logger = logging.getLogger("gfps.api")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:1420,http://localhost:3000"
    ).split(",")
    if origin.strip()
]
if not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = ["http://localhost:1420"]

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RateLimiter:
    def __init__(self, limit: int, window_sec: int) -> None:
        self.limit = limit
        self.window_sec = window_sec
        self.hits: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        if self.limit <= 0:
            return True
        now = time.time()
        window_start = now - self.window_sec
        bucket = self.hits.setdefault(key, deque())
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE, RATE_LIMIT_WINDOW_SEC)


@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    if request.url.path.startswith(("/health", "/docs", "/openapi.json", "/ws")):
        return await call_next(request)
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    key = client_ip or (request.client.host if request.client else "unknown")
    if not rate_limiter.allow(key):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_override(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# -------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    # Create all DB tables if they don't exist
    Base.metadata.create_all(bind=engine)

    if SECRET_KEY == "change-this-secret":
        logger.warning("SECRET_KEY is using the default value; set it in production.")

    # Ensure seed snapshots are persisted for offline use
    backfill_seed_if_empty()

    # Start background workers (alerts + live streamer)
    loop = asyncio.get_running_loop()
    start_alert_engine_background(loop)
    start_streamer_background(loop)
    start_snapshot_scheduler(loop)
    start_odds_snapshot_scheduler(loop)


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
app.include_router(health_router)
app.include_router(markets_router)
app.include_router(coupon_router)
app.include_router(analysis_router)
app.include_router(favorites_router)
app.include_router(device_router)
app.include_router(stats_router)
app.include_router(alerts_router)
app.include_router(pipeline_router)
app.include_router(replay_router)
app.include_router(observability_router)
app.include_router(xg_router)
app.include_router(performance_router)


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
