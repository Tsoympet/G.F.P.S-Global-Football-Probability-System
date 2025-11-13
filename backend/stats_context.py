from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import TeamStats


def build_poisson_context(
    db: Session,
    league_id: str,
    home_team: str,
    away_team: str,
    season: str = "2024",
) -> dict:
    ctx: dict = {}

    home = db.scalar(
        select(TeamStats).where(
            TeamStats.league_id == league_id,
            TeamStats.team_name == home_team,
            TeamStats.season == season,
        )
    )
    away = db.scalar(
        select(TeamStats).where(
            TeamStats.league_id == league_id,
            TeamStats.team_name == away_team,
            TeamStats.season == season,
        )
    )

    if home and away:
        ctx["home_attack"] = home.home_attack
        ctx["away_attack"] = away.away_attack
        ctx["home_defense"] = home.home_defense
        ctx["away_defense"] = away.away_defense
        ctx["avg_goals_home_league"] = home.avg_goals_for
        ctx["avg_goals_away_league"] = away.avg_goals_for

    return ctx
