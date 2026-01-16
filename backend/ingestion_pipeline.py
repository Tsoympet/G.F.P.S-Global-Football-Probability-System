from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from .data_normalization import normalize_fixture
from .data_providers import KeyBasedStubProvider, OpenFootballCSVProvider, Provider
from .data_quality import (
    confidence_score,
    deduplicate_records,
    detect_anomalies,
    validate_fixture_schema,
    validate_result_schema,
)
from .db import SessionLocal, engine
from .feature_builder import build_match_features
from .models import EventEntity, FixtureEntity, LineupEntity, ResultEntity
from .storage import (
    ensure_schema,
    record_ingestion_run,
    upsert_events,
    upsert_fixture,
    upsert_lineups,
    upsert_result,
)
from .storage.cache import TTLCache


def _default_providers() -> list[Provider]:
    providers: list[Provider] = [OpenFootballCSVProvider()]
    stub = KeyBasedStubProvider()
    if stub.api_key:
        providers.append(stub)
    return providers


def _session_factory_for_engine(db_engine):
    if db_engine is engine:
        return SessionLocal
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)


def ingest_fixtures(
    session: Optional[Session] = None,
    providers: Optional[list[Provider]] = None,
    db_engine=engine,
) -> dict:
    ensure_schema(db_engine)
    stats = {"fixtures": 0, "results": 0, "anomalies": 0}
    local_session = session or _session_factory_for_engine(db_engine)()

    for provider in providers or _default_providers():
        run_status = "completed"
        try:
            fixtures = [
                normalize_fixture(validate_fixture_schema(fixture))
                for fixture in provider.get_fixtures()
            ]
            fixtures = deduplicate_records(
                fixtures,
                key_func=lambda f: f.fixture_id,
                confidence_func=lambda f: confidence_score(f, source_priority=1),
            )
            for fx in fixtures:
                upsert_fixture(
                    local_session,
                    FixtureEntity(
                        fixture_id=fx.fixture_id,
                        provider=provider.meta.name,
                        league=fx.league,
                        season=fx.season,
                        home_team=fx.home_team,
                        away_team=fx.away_team,
                        kickoff_utc=fx.kickoff,
                        venue=fx.venue,
                    ),
                )
                stats["fixtures"] += 1

            results = [
                validate_result_schema(result) for result in provider.get_results()
            ]
            results = deduplicate_records(
                results,
                key_func=lambda r: r.fixture_id,
                confidence_func=lambda r: confidence_score(r, source_priority=2),
            )
            for res in results:
                anomalies = detect_anomalies(res)
                if anomalies:
                    stats["anomalies"] += len(anomalies)
                    continue
                upsert_result(
                    local_session,
                    ResultEntity(
                        fixture_id=res.fixture_id,
                        provider=provider.meta.name,
                        home_score=res.home_score,
                        away_score=res.away_score,
                        status=res.status,
                    ),
                )
                stats["results"] += 1
            record_ingestion_run(local_session, provider.meta.name, stats=stats)
            local_session.commit()
        except Exception:
            run_status = "failed"
            local_session.rollback()
            record_ingestion_run(local_session, provider.meta.name, stats=stats, status=run_status)
            local_session.commit()
            raise
    return stats


def ingest_live(
    session: Optional[Session] = None,
    providers: Optional[list[Provider]] = None,
    cache: Optional[TTLCache] = None,
    db_engine=engine,
):
    ensure_schema(db_engine)
    local_session = session or _session_factory_for_engine(db_engine)()
    cache = cache or TTLCache()
    for provider in providers or _default_providers():
        if not provider.meta.supports_live:
            continue
        events = list(provider.get_live_events())
        events_payload = [e.model_dump() for e in events] if events else []
        if events_payload:
            key = f"{provider.meta.name}-events"
            cached = cache.get(key)
            if cached == events_payload:
                continue
            cache.set(key, events_payload)
        upsert_events(
            local_session,
            [
                EventEntity(
                    fixture_id=ev.fixture_id,
                    minute=ev.minute,
                    team=ev.team,
                    type=ev.type,
                    player=ev.player,
                )
                for ev in events
            ],
        )
        upsert_lineups(
            local_session,
            [
                LineupEntity(fixture_id=lu.fixture_id, team=lu.team, players=lu.players)
                for lu in provider.get_lineups()
            ],
        )
    local_session.commit()


def build_features(
    session: Optional[Session] = None,
    fixture_ids: Optional[list[str]] = None,
    db_engine=engine,
) -> dict[str, dict]:
    ensure_schema(db_engine)
    local_session = session or _session_factory_for_engine(db_engine)()
    results: dict[str, dict] = {}
    ids = fixture_ids
    if not ids:
        ids = [row[0] for row in local_session.query(FixtureEntity.fixture_id).all()]
    for fixture_id in ids:
        results[fixture_id] = build_match_features(local_session, fixture_id)
    local_session.commit()
    return results
