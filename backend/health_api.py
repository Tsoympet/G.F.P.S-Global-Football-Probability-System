from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter
from sqlalchemy import text

from .db import engine

router = APIRouter(prefix="/health", tags=["health"])


START_TIME = datetime.utcnow()


def _check_database() -> Dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pylint: disable=broad-except
        return {"status": "error", "detail": str(exc)}


@router.get("")
async def health() -> Dict[str, Any]:
    db_status = _check_database()
    ok = db_status.get("status") == "ok"

    return {
        "ok": ok,
        "uptime_sec": (datetime.utcnow() - START_TIME).total_seconds(),
        "services": {
            "api": {"status": "ok"},
            "database": db_status,
        },
    }
