from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session
from sqlalchemy import select

from .auth_dependency import require_user
from .db import SessionLocal
from .models import TeamStats

router = APIRouter(prefix="/stats", tags=["stats"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TeamStatsIn(BaseModel):
    league_id: constr(min_length=1)
    league_name: constr(min_length=1)
    team_name: constr(min_length=1)
    season: constr(min_length=4, max_length=8) = "2024"
    home_attack: float = Field(default=1.0, gt=0.0)
    away_attack: float = Field(default=1.0, gt=0.0)
    home_defense: float = Field(default=1.0, gt=0.0)
    away_defense: float = Field(default=1.0, gt=0.0)
    avg_goals_for: float = Field(default=1.5, gt=0.0)
    avg_goals_against: float = Field(default=1.2, gt=0.0)


@router.post("/team/upsert", dependencies=[Depends(require_user)])
def upsert_team_stats(p: TeamStatsIn, db: Session = Depends(get_db)):
    row = db.scalar(
        select(TeamStats).where(
            TeamStats.league_id == p.league_id,
            TeamStats.team_name == p.team_name,
            TeamStats.season == p.season,
        )
    )
    if not row:
        row = TeamStats(
            league_id=p.league_id,
            league_name=p.league_name,
            team_name=p.team_name,
            season=p.season,
        )

    row.home_attack = p.home_attack
    row.away_attack = p.away_attack
    row.home_defense = p.home_defense
    row.away_defense = p.away_defense
    row.avg_goals_for = p.avg_goals_for
    row.avg_goals_against = p.avg_goals_against

    db.add(row)
    db.commit()
    db.refresh(row)
    return {"ok": True, "id": row.id}


@router.get("/team", dependencies=[Depends(require_user)])
def get_team_stats(league_id: str, team_name: str, season: str = "2024", db: Session = Depends(get_db)):
    row = db.scalar(
        select(TeamStats).where(
            TeamStats.league_id == league_id,
            TeamStats.team_name == team_name,
            TeamStats.season == season,
        )
    )
    if not row:
        raise HTTPException(404, "No stats found")
    return {
        "ok": True,
        "item": {
            "league_id": row.league_id,
            "league_name": row.league_name,
            "team_name": row.team_name,
            "season": row.season,
            "home_attack": row.home_attack,
            "away_attack": row.away_attack,
            "home_defense": row.home_defense,
            "away_defense": row.away_defense,
            "avg_goals_for": row.avg_goals_for,
            "avg_goals_against": row.avg_goals_against,
        },
    }
