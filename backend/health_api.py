import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from sqlalchemy import text

from .db import engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


START_TIME = datetime.now(timezone.utc)


def _check_database() -> Dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:  # pylint: disable=broad-except
        logger.exception("Database health check failed")
        return {"status": "error", "detail": "Database connection failed"}


@router.get("")
async def health() -> Dict[str, Any]:
    db_status = _check_database()
    ok = db_status.get("status") == "ok"

    return {
        "ok": ok,
        "uptime_sec": (datetime.now(timezone.utc) - START_TIME).total_seconds(),
        "services": {
            "api": {"status": "ok"},
            "database": db_status,
        },
    }
