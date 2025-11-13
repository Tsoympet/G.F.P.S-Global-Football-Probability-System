from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import User, FavoriteLeague, FavoriteTeam
from .auth_utils import decode_token

router = APIRouter(prefix="/favorites", tags=["favorites"])


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


class FavLeagueIn(BaseModel):
    token: str
    league_id: str
    league_name: str


class FavTeamIn(BaseModel):
    token: str
    team_id: str
    team_name: str
    league_id: str | None = None
    league_name: str | None = None


@router.post("/league")
def add_league(p: FavLeagueIn, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    existing = db.scalar(
        select(FavoriteLeague).where(
            FavoriteLeague.user_id == user.id,
            FavoriteLeague.league_id == p.league_id,
        )
    )
    if existing:
        return {"ok": True, "id": existing.id}
    fl = FavoriteLeague(
        user_id=user.id,
        league_id=p.league_id,
        league_name=p.league_name,
    )
    db.add(fl)
    db.commit()
    db.refresh(fl)
    return {"ok": True, "id": fl.id}


@router.get("/leagues")
def list_leagues(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    rows = db.scalars(select(FavoriteLeague).where(FavoriteLeague.user_id == user.id)).all()
    return {
        "ok": True,
        "items": [
            {"id": r.id, "league_id": r.league_id, "league_name": r.league_name}
            for r in rows
        ],
    }


@router.delete("/league/{fav_id}")
def delete_league(fav_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    r = db.scalar(
        select(FavoriteLeague).where(FavoriteLeague.id == fav_id, FavoriteLeague.user_id == user.id)
    )
    if not r:
        raise HTTPException(404, "Not found")
    db.delete(r)
    db.commit()
    return {"ok": True}


@router.post("/team")
def add_team(p: FavTeamIn, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    existing = db.scalar(
        select(FavoriteTeam).where(
            FavoriteTeam.user_id == user.id,
            FavoriteTeam.team_id == p.team_id,
        )
    )
    if existing:
        return {"ok": True, "id": existing.id}
    ft = FavoriteTeam(
        user_id=user.id,
        team_id=p.team_id,
        team_name=p.team_name,
        league_id=p.league_id or "",
        league_name=p.league_name or "",
    )
    db.add(ft)
    db.commit()
    db.refresh(ft)
    return {"ok": True, "id": ft.id}


@router.get("/teams")
def list_teams(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    rows = db.scalars(select(FavoriteTeam).where(FavoriteTeam.user_id == user.id)).all()
    return {
        "ok": True,
        "items": [
            {
                "id": r.id,
                "team_id": r.team_id,
                "team_name": r.team_name,
                "league_id": r.league_id,
                "league_name": r.league_name,
            }
            for r in rows
        ],
    }


@router.delete("/team/{fav_id}")
def delete_team(fav_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    r = db.scalar(
        select(FavoriteTeam).where(FavoriteTeam.id == fav_id, FavoriteTeam.user_id == user.id)
    )
    if not r:
        raise HTTPException(404, "Not found")
    db.delete(r)
    db.commit()
    return {"ok": True}
