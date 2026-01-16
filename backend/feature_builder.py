from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import FixtureEntity, ResultEntity
from .storage import save_features


def _team_results(session: Session, team: str, limit: int = 5):
    rows = session.execute(
        select(ResultEntity, FixtureEntity)
        .join(FixtureEntity, ResultEntity.fixture_id == FixtureEntity.fixture_id)
        .where(or_(FixtureEntity.home_team == team, FixtureEntity.away_team == team))
        .order_by(FixtureEntity.kickoff_utc.desc())
        .limit(limit)
    ).all()
    return rows


def rolling_xg_proxy(rows: Iterable[tuple[ResultEntity, FixtureEntity]], team: str) -> dict:
    goals_for = []
    goals_against = []
    for result, fixture in rows:
        if fixture.home_team == team:
            goals_for.append(result.home_score)
            goals_against.append(result.away_score)
        else:
            goals_for.append(result.away_score)
            goals_against.append(result.home_score)
    if not goals_for:
        return {"for": 0.0, "against": 0.0}
    return {
        "for": sum(goals_for) / len(goals_for),
        "against": sum(goals_against) / len(goals_against),
    }


def form_score(rows: Iterable[tuple[ResultEntity, FixtureEntity]], team: str) -> float:
    # EWMA with decay 0.8 favouring recent form
    score = 0.0
    weight = 1.0
    total_weight = 0.0
    for result, fixture in rows:
        if result.home_score == result.away_score:
            outcome = 1
        elif (fixture.home_team == team and result.home_score > result.away_score) or (
            fixture.away_team == team and result.away_score > result.home_score
        ):
            outcome = 3
        else:
            outcome = 0
        score += outcome * weight
        total_weight += weight
        weight *= 0.8
    return score / total_weight if total_weight else 0.0


def rest_days(rows: Iterable[tuple[ResultEntity, FixtureEntity]], reference: datetime) -> float:
    closest = float("inf")
    for _, fixture in rows:
        delta = reference - fixture.kickoff_utc
        days = delta.total_seconds() / 86400
        if days > 0:
            closest = min(closest, days)
    return closest


def poisson_lambda(goal_rate: float) -> float:
    return max(0.1, goal_rate)


def build_match_features(session: Session, fixture_id: str, reference_time: datetime | None = None) -> dict:
    fixture = session.scalar(select(FixtureEntity).where(FixtureEntity.fixture_id == fixture_id))
    if not fixture:
        raise ValueError("fixture not found")
    home_rows = _team_results(session, fixture.home_team)
    away_rows = _team_results(session, fixture.away_team)

    home_xg = rolling_xg_proxy(home_rows, fixture.home_team)
    away_xg = rolling_xg_proxy(away_rows, fixture.away_team)

    home_form = form_score(home_rows, fixture.home_team)
    away_form = form_score(away_rows, fixture.away_team)

    reference_time = reference_time or fixture.kickoff_utc
    features = {
        "fixture_id": fixture.fixture_id,
        "home_team": fixture.home_team,
        "away_team": fixture.away_team,
        "home_xg_proxy": home_xg,
        "away_xg_proxy": away_xg,
        "home_form": home_form,
        "away_form": away_form,
        "home_rest_days": rest_days(home_rows, reference_time),
        "away_rest_days": rest_days(away_rows, reference_time),
        "lambda_home": poisson_lambda(home_xg["for"]),
        "lambda_away": poisson_lambda(away_xg["for"]),
    }
    save_features(session, fixture.fixture_id, features)
    return features
