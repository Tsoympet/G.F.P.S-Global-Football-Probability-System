from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import User, Coupon, CouponSelection
from .auth_utils import decode_token
from .prediction_engine import predict_market
from .stats_context import build_poisson_context

router = APIRouter(prefix="/coupon", tags=["coupon"])


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


class SelectionIn(BaseModel):
    fixture_id: str
    league: str
    league_id: str
    home: str
    away: str
    market: str
    outcome: str
    odds: float
    prob: float | None = None


class CouponCreate(BaseModel):
    token: str
    name: str
    selections: List[SelectionIn]


@router.post("/create")
def create_coupon(p: CouponCreate, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    if not p.selections:
        raise HTTPException(400, "No selections")

    total_odds = 1.0
    total_prob = 1.0
    selections_data = []

    for s in p.selections:
        ctx = build_poisson_context(db, s.league_id, s.home, s.away)
        if s.prob is None or s.prob <= 0 or s.prob >= 1:
            preds = predict_market(
                s.market,
                {s.outcome: s.odds},
                ctx,
            )
            info = preds[s.outcome]
            prob = info["prob"]
            ev = info["ev"]
        else:
            prob = s.prob
            ev = prob * s.odds - 1.0

        total_odds *= s.odds
        total_prob *= prob

        selections_data.append((s, prob, ev))

    total_ev = total_prob * total_odds - 1.0

    coupon = Coupon(
        user_id=user.id,
        name=p.name,
        status="draft",
        total_odds=total_odds,
        total_prob=total_prob,
        total_ev=total_ev,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    for s, prob, ev in selections_data:
        cs = CouponSelection(
            coupon_id=coupon.id,
            fixture_id=s.fixture_id,
            league=s.league,
            league_id=s.league_id,
            home=s.home,
            away=s.away,
            market=s.market,
            outcome=s.outcome,
            odds=s.odds,
            prob=prob,
            ev=ev,
        )
        db.add(cs)
    db.commit()

    return {
        "ok": True,
        "id": coupon.id,
        "total_odds": coupon.total_odds,
        "total_prob": coupon.total_prob,
        "total_ev": coupon.total_ev,
    }


@router.get("/list")
def list_coupons(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    coupons = (
        db.scalars(
            select(Coupon)
            .where(Coupon.user_id == user.id)
            .order_by(Coupon.id.desc())
        ).all()
    )
    out = []
    for c in coupons:
        out.append(
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "total_odds": c.total_odds,
                "total_prob": c.total_prob,
                "total_ev": c.total_ev,
                "created_at": str(c.created_at),
            }
        )
    return {"ok": True, "items": out}


@router.get("/{coupon_id}")
def get_coupon(coupon_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    c = db.scalar(
        select(Coupon).where(Coupon.id == coupon_id, Coupon.user_id == user.id)
    )
    if not c:
        raise HTTPException(404, "Coupon not found")

    sels = db.scalars(
        select(CouponSelection).where(CouponSelection.coupon_id == coupon_id)
    ).all()

    return {
        "ok": True,
        "id": c.id,
        "name": c.name,
        "status": c.status,
        "total_odds": c.total_odds,
        "total_prob": c.total_prob,
        "total_ev": c.total_ev,
        "created_at": str(c.created_at),
        "selections": [
            {
                "fixture_id": s.fixture_id,
                "league": s.league,
                "league_id": s.league_id,
                "home": s.home,
                "away": s.away,
                "market": s.market,
                "outcome": s.outcome,
                "odds": s.odds,
                "prob": s.prob,
                "ev": s.ev,
            }
            for s in sels
        ],
    }


@router.delete("/{coupon_id}")
def delete_coupon(coupon_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    c = db.scalar(
        select(Coupon).where(Coupon.id == coupon_id, Coupon.user_id == user.id)
    )
    if not c:
        raise HTTPException(404, "Coupon not found")

    db.query(CouponSelection).filter(CouponSelection.coupon_id == coupon_id).delete()
    db.delete(c)
    db.commit()
    return {"ok": True}
