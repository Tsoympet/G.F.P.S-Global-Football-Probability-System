from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .data_normalization import normalize_fixture
from .data_providers import (
    ApiFootballProvider,
    DataSourceSettings,
    FootballDataOrgProvider,
    KeyBasedStubProvider,
    OpenFootballCSVProvider,
    OpenLigaDBLiveProvider,
    Provider,
    ProviderRegistry,
    WebScraperProvider,
    load_settings_from_env,
)
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
def _build_registry(settings: Optional[DataSourceSettings] = None) -> ProviderRegistry:
    settings = settings or load_settings_from_env()
    registry = ProviderRegistry(settings)
    registry.register(OpenFootballCSVProvider())
    registry.register(FootballDataOrgProvider(api_key=settings.api_keys.get("football-data.org"), allow_network=settings.live_network_enabled))
    registry.register(WebScraperProvider(allow_network=settings.live_network_enabled))
    registry.register(OpenLigaDBLiveProvider(allow_network=settings.live_network_enabled))
    registry.register(ApiFootballProvider(api_key=settings.api_keys.get("api-football-premium")))
    registry.register(KeyBasedStubProvider())
    return registry


def _session_factory_for_engine(db_engine):
    if getattr(db_engine, "url", None) == getattr(engine, "url", None):
        return SessionLocal
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)


def ingest_fixtures(
    session: Optional[Session] = None,
    providers: Optional[list[Provider]] = None,
    db_engine=engine,
    settings: Optional[DataSourceSettings] = None,
) -> dict:
    ensure_schema(db_engine)
    stats = {"fixtures": 0, "results": 0, "anomalies": 0}
    local_session = session or _session_factory_for_engine(db_engine)()
    registry = _build_registry(settings)
    active_providers = (
        [(p, getattr(p.meta, "reliability", 0.5)) for p in providers]
        if providers is not None
        else [(p, registry.reliability(p)) for p in registry.active(data_types={"fixtures", "results"})]
    )
    for provider, source_weight in active_providers:
        run_status = "completed"
        try:
            fixtures = [
                normalize_fixture(validate_fixture_schema(fixture))
                for fixture in provider.get_fixtures()
            ]
            fixtures = deduplicate_records(
                fixtures,
                key_func=lambda f: f.fixture_id,
                confidence_func=lambda f: confidence_score(f, source_priority=source_weight),
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
                confidence_func=lambda r: confidence_score(r, source_priority=source_weight),
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
        except (SQLAlchemyError, ValueError) as exc:
            run_status = "failed"
            local_session.rollback()
            record_ingestion_run(local_session, provider.meta.name, stats=stats, status=run_status)
            local_session.commit()
            raise exc
    return stats


def ingest_live(
    session: Optional[Session] = None,
    providers: Optional[list[Provider]] = None,
    cache: Optional[TTLCache] = None,
    db_engine=engine,
    settings: Optional[DataSourceSettings] = None,
):
    ensure_schema(db_engine)
    local_session = session or _session_factory_for_engine(db_engine)()
    cache = cache or TTLCache()
    registry = _build_registry(settings)
    active_providers = providers or list(registry.active(data_types={"live_events", "fixtures"}, live_only=True))
    for provider in active_providers:
        if not provider.meta.supports_live:
            continue
        events = list(provider.get_live_events())
        if events:
            key = f"{provider.meta.name}-events"
            cached = cache.get(key)
            events_payload = [e.model_dump() for e in events]
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
