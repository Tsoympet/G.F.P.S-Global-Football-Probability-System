import asyncio
import os
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import AlertRule, AlertEvent, User, Device
from .prediction_engine import predict_market
from .push_notify import send_fcm_push
from .stats_context import build_poisson_context

ALERT_ENGINE_ENABLED = os.getenv("ALERT_ENGINE", "false").lower() in ("1", "true", "yes")
ALERT_ENGINE_INTERVAL_SEC = int(os.getenv("ALERT_ENGINE_INTERVAL_SEC", "60"))


async def fetch_live_candidates() -> list[dict]:
    """
    Placeholder: in real use, call external APIs (like API-Football)
    to get fixtures + odds to evaluate for alerts.
    For now, returns empty list.
    """
    return []


def evaluate_rule(rule: AlertRule, candidate: dict, db: Session) -> Optional[AlertEvent]:
    """
    Given a rule and a candidate fixture+market, decide if it triggers.
    This is just a skeleton; fill with real logic when wiring live odds.
    """
    return None  # no-op for now


async def alert_worker_loop():
    if not ALERT_ENGINE_ENABLED:
        print("[alert_engine] Disabled via ALERT_ENGINE env")
        return

    print("[alert_engine] Started")
    while True:
        try:
            candidates = await fetch_live_candidates()
            if not candidates:
                await asyncio.sleep(ALERT_ENGINE_INTERVAL_SEC)
                continue

            with SessionLocal() as db:
                rules = db.scalars(select(AlertRule).where(AlertRule.is_active == True)).all()
                for cand in candidates:
                    for rule in rules:
                        evt = evaluate_rule(rule, cand, db)
                        if not evt:
                            continue
                        db.add(evt)
                        db.commit()
                        db.refresh(evt)

                        # push to user's devices (if any)
                        devices = db.scalars(
                            select(Device).where(Device.user_id == rule.user_id)
                        ).all()
                        tokens = [d.token for d in devices if d.platform in ("android", "ios")]
                        if tokens:
                            body = f"Alert triggered for rule {rule.name}"
                            await send_fcm_push(
                                tokens,
                                title="GFPS Alert",
                                body=body,
                                data={"event_id": evt.id},
                            )

        except Exception as e:
            print("[alert_engine] ERROR:", e)

        await asyncio.sleep(ALERT_ENGINE_INTERVAL_SEC)


def start_alert_engine_background(loop: asyncio.AbstractEventLoop):
    if not ALERT_ENGINE_ENABLED:
        return
    loop.create_task(alert_worker_loop())
