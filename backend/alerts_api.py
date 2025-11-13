from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import AlertRule, AlertEvent, User
from .auth_utils import decode_token

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(token: str, db: Session) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    email = payload.get("sub")
    u = db.scalar(select(User).where(User.email == email))
    if not u:
        raise HTTPException(404, "User not found")
    return u


class AlertRuleIn(BaseModel):
    token: str
    name: str
    league_filter: Optional[str] = None
    team_filter: Optional[str] = None
    market_filter: Optional[str] = None
    outcome_filter: Optional[str] = None
    min_odds: Optional[float] = None
    max_odds: Optional[float] = None
    min_ev: Optional[float] = None
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    token: str
    name: Optional[str] = None
    league_filter: Optional[str] = None
    team_filter: Optional[str] = None
    market_filter: Optional[str] = None
    outcome_filter: Optional[str] = None
    min_odds: Optional[float] = None
    max_odds: Optional[float] = None
    min_ev: Optional[float] = None
    is_active: Optional[bool] = None


@router.post("/rules")
def create_rule(p: AlertRuleIn, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    r = AlertRule(
        user_id=user.id,
        name=p.name,
        league_filter=p.league_filter,
        team_filter=p.team_filter,
        market_filter=p.market_filter,
        outcome_filter=p.outcome_filter,
        min_odds=p.min_odds,
        max_odds=p.max_odds,
        min_ev=p.min_ev,
        is_active=p.is_active,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"ok": True, "id": r.id}


@router.get("/rules")
def list_rules(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    rows = db.scalars(select(AlertRule).where(AlertRule.user_id == user.id)).all()
    return {
        "ok": True,
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "league_filter": r.league_filter,
                "team_filter": r.team_filter,
                "market_filter": r.market_filter,
                "outcome_filter": r.outcome_filter,
                "min_odds": r.min_odds,
                "max_odds": r.max_odds,
                "min_ev": r.min_ev,
                "is_active": r.is_active,
            }
            for r in rows
        ],
    }


@router.patch("/rules/{rule_id}")
def update_rule(rule_id: int, p: AlertRuleUpdate, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    r = db.scalar(
        select(AlertRule).where(AlertRule.id == rule_id, AlertRule.user_id == user.id)
    )
    if not r:
        raise HTTPException(404, "Rule not found")

    if p.name is not None:
        r.name = p.name
    if p.league_filter is not None:
        r.league_filter = p.league_filter
    if p.team_filter is not None:
        r.team_filter = p.team_filter
    if p.market_filter is not None:
        r.market_filter = p.market_filter
    if p.outcome_filter is not None:
        r.outcome_filter = p.outcome_filter
    if p.min_odds is not None:
        r.min_odds = p.min_odds
    if p.max_odds is not None:
        r.max_odds = p.max_odds
    if p.min_ev is not None:
        r.min_ev = p.min_ev
    if p.is_active is not None:
        r.is_active = p.is_active

    db.add(r)
    db.commit()

    return {"ok": True}


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    r = db.scalar(
        select(AlertRule).where(AlertRule.id == rule_id, AlertRule.user_id == user.id)
    )
    if not r:
        raise HTTPException(404, "Rule not found")
    db.delete(r)
    db.commit()
    return {"ok": True}


@router.get("/events")
def list_events(token: str, limit: int = 50, db: Session = Depends(get_db)):
    user = get_user(token, db)
    q = (
        db.query(AlertEvent)
        .filter(AlertEvent.user_id == user.id)
        .order_by(AlertEvent.id.desc())
        .limit(limit)
    )
    events = q.all()
    return {
        "ok": True,
        "items": [
            {
                "id": e.id,
                "rule_id": e.rule_id,
                "fixture_id": e.fixture_id,
                "market": e.market,
                "outcome": e.outcome,
                "odds": e.odds,
                "prob": e.prob,
                "ev": e.ev,
                "meta": e.meta,
                "created_at": str(e.created_at),
            }
            for e in events
        ],
    }
