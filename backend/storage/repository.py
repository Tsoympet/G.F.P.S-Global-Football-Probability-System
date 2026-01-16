from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    Base,
    EventEntity,
    FixtureEntity,
    IngestionRunEntity,
    LineupEntity,
    ModelFeatureEntity,
    ResultEntity,
)


def _add_in_batches(session: Session, items: Iterable, batch_size: int = 500) -> None:
    batch: list = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            session.add_all(batch)
            batch.clear()
    if batch:
        session.add_all(batch)


def ensure_schema(engine) -> None:
    Base.metadata.create_all(bind=engine)


def upsert_fixture(session: Session, fixture: FixtureEntity) -> FixtureEntity:
    existing = session.scalar(select(FixtureEntity).where(FixtureEntity.fixture_id == fixture.fixture_id))
    if existing:
        for field in ["league", "season", "home_team", "away_team", "kickoff_utc", "venue", "provider"]:
            setattr(existing, field, getattr(fixture, field))
        return existing
    session.add(fixture)
    return fixture


def upsert_result(session: Session, result: ResultEntity) -> ResultEntity:
    existing = session.scalar(
        select(ResultEntity).where(
            ResultEntity.fixture_id == result.fixture_id, ResultEntity.provider == result.provider
        )
    )
    if existing:
        existing.home_score = result.home_score
        existing.away_score = result.away_score
        existing.status = result.status
        return existing
    session.add(result)
    return result


def upsert_events(session: Session, events: Iterable[EventEntity]) -> None:
    _add_in_batches(session, events)


def upsert_lineups(session: Session, lineups: Iterable[LineupEntity]) -> None:
    _add_in_batches(session, lineups)


def save_features(session: Session, fixture_id: str, payload: dict) -> ModelFeatureEntity:
    existing = session.scalar(select(ModelFeatureEntity).where(ModelFeatureEntity.fixture_id == fixture_id))
    if existing:
        existing.payload = payload
        return existing
    entity = ModelFeatureEntity(fixture_id=fixture_id, payload=payload)
    session.add(entity)
    return entity


def record_ingestion_run(session: Session, provider: str, stats: dict | None = None, status: str = "completed"):
    run = IngestionRunEntity(
        provider=provider,
        completed_at=datetime.now(timezone.utc),
        status=status,
        stats=stats,
    )
    session.add(run)
    return run
