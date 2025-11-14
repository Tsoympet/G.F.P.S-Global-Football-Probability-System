"""
backend/value_api.py

Endpoints για EV+ value picks.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from .db import SessionLocal
from .models import ValuePick
from .auth_utils import get_current_user  # αν έχεις JWT auth

router = APIRouter(prefix="/value-picks", tags=["value-picks"])


class ValuePickOut(BaseModel):
    id: int
    fixture_id: str
    league: str
    league_id: str
    home: str
    away: str
    bookmaker: str
    market: str
    outcome: str
    odds: float
    prob: float
    ev: float
    created_at: str

    class Config:
        orm_mode = True


@router.get("/", response_model=List[ValuePickOut])
def list_value_picks(
    min_ev: float = Query(0.05, description="Minimum EV threshold"),
    league: Optional[str] = Query(None, description="League filter (contains)"),
    bookmaker: Optional[str] = Query(None, description="Bookmaker filter (contains)"),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
):
    db = SessionLocal()
    try:
        q = db.query(ValuePick).filter(ValuePick.ev >= min_ev)
        if league:
            q = q.filter(ValuePick.league.ilike(f"%{league}%"))
        if bookmaker:
            q = q.filter(ValuePick.bookmaker.ilike(f"%{bookmaker}%"))

        q = q.order_by(ValuePick.ev.desc(), ValuePick.created_at.desc())
        rows = q.limit(limit).all()
        return rows
    finally:
        db.close()
