"""
G.F.P.S – Global Football Probability System
Backend API (FastAPI)
"""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket

from .db import Base, engine
from . import models  # noqa: F401 (ensure models are imported)
from .google_auth import router as auth_router
from .fixtures_api import router as fixtures_router
from .markets_api import router as markets_router
from .coupon_api import router as coupon_router
from .favorites_api import router as favorites_router
from .device_api import router as device_router
from .stats_api import router as stats_router
from .chat_api import router as chat_router
from .chat_ws import chat_ws_handler
from .alert_engine import start_alert_engine_background
from .streamer import start_streamer_background

app = FastAPI(
    title="GFPS – Global Football Probability System",
    version="0.1.0",
)

# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # create tables
    Base.metadata.create_all(bind=engine)

    loop = asyncio.get_event_loop()
    start_alert_engine_background(loop)
    start_streamer_background(loop)


# Routers
app.include_router(auth_router)
app.include_router(fixtures_router)
app.include_router(markets_router)
app.include_router(coupon_router)
app.include_router(favorites_router)
app.include_router(device_router)
app.include_router(stats_router)
app.include_router(chat_router)


@app.websocket("/ws/chat")
async def chat_socket(ws: WebSocket):
    await chat_ws_handler(ws)
