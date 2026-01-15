from typing import List

from fastapi import APIRouter, Depends, HTTPException
from dataclasses import dataclass
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import User, Coupon, CouponSelection
from .auth_dependency import require_user
from .prediction_engine import predict_market
from .stats_context import build_poisson_context
from .validation import require_decimal_odds
from .value.ev import expected_value


@dataclass(frozen=True)
class SelectionSummary:
    selection: "SelectionIn"
    odds: float
    prob: float
    ev: float

router = APIRouter(prefix="/coupon", tags=["coupon"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SelectionIn(BaseModel):
    fixture_id: constr(min_length=1)
    league: constr(min_length=1)
    league_id: constr(min_length=1)
    home: constr(min_length=1)
    away: constr(min_length=1)
    market: constr(min_length=1)
    outcome: constr(min_length=1)
    odds: float = Field(gt=1.0)
    prob: float | None = Field(default=None, gt=0.0, lt=1.0)


class CouponCreate(BaseModel):
    name: constr(min_length=1)
    selections: List[SelectionIn]


@router.post("/create")
def create_coupon(p: CouponCreate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not p.selections:
        raise HTTPException(400, "No selections")

    total_odds = 1.0
    total_prob = 1.0
    selections_data: List[SelectionSummary] = []

    for s in p.selections:
        ctx = build_poisson_context(db, s.league_id, s.home, s.away)
        odds = require_decimal_odds(s.odds, "selection odds")
        if s.prob is None or s.prob <= 0 or s.prob >= 1:
            preds = predict_market(
                s.market,
                {s.outcome: odds},
                ctx,
            )
            info = preds.get(s.outcome)
            if not info:
                raise HTTPException(422, f"No probability available for {s.outcome}")
            prob = info["prob"]
            ev = info["ev"]
        else:
            prob = s.prob
            ev = expected_value(prob, odds)

        total_odds *= odds
        total_prob *= prob

        selections_data.append(SelectionSummary(selection=s, odds=odds, prob=prob, ev=ev))

    total_ev = expected_value(total_prob, total_odds)

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

    for summary in selections_data:
        s = summary.selection
        cs = CouponSelection(
            coupon_id=coupon.id,
            fixture_id=s.fixture_id,
            league=s.league,
            league_id=s.league_id,
            home=s.home,
            away=s.away,
            market=s.market,
            outcome=s.outcome,
            odds=summary.odds,
            prob=summary.prob,
            ev=summary.ev,
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
def list_coupons(user: User = Depends(require_user), db: Session = Depends(get_db)):
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
def get_coupon(coupon_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
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
def delete_coupon(coupon_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    c = db.scalar(
        select(Coupon).where(Coupon.id == coupon_id, Coupon.user_id == user.id)
    )
    if not c:
        raise HTTPException(404, "Coupon not found")

    db.query(CouponSelection).filter(CouponSelection.coupon_id == coupon_id).delete()
    db.delete(c)
    db.commit()
    return {"ok": True}
