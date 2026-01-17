from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .db import Base


def _empty_fixture_list() -> list[str]:
    return []


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # API usage tracking for pay-per-use model
    api_calls_count: Mapped[int] = mapped_column(Integer, default=0)
    api_calls_last_reset: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)

    # token version – if incremented, old JWTs become invalid
    token_version: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # password reset fields
    reset_token: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    reset_token_exp: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)

    # simple 2FA fields (not fully wired yet)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_secret: Mapped[Optional[str]] = mapped_column(String(64), default=None)

    devices: Mapped[list["Device"]] = relationship(back_populates="user")
    coupons: Mapped[list["Coupon"]] = relationship(back_populates="user")
    alert_rules: Mapped[list["AlertRule"]] = relationship(back_populates="user")
    alert_events: Mapped[list["AlertEvent"]] = relationship(back_populates="user")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(32))  # android / ios / web
    token: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="devices")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))

    league_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    team_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    market_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    outcome_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)

    min_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    max_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    min_ev: Mapped[Optional[float]] = mapped_column(Float, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="alert_rules")
    events: Mapped[list["AlertEvent"]] = relationship(back_populates="rule")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("alert_rules.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    fixture_id: Mapped[str] = mapped_column(String(64))
    market: Mapped[str] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(128))
    odds: Mapped[float] = mapped_column(Float)
    prob: Mapped[float] = mapped_column(Float)
    ev: Mapped[float] = mapped_column(Float)

    meta: Mapped[Optional[dict]] = mapped_column(JSON, default=None)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    rule: Mapped["AlertRule"] = relationship(back_populates="events")
    user: Mapped["User"] = relationship(back_populates="alert_events")


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft / open / won / lost / canceled

    total_odds: Mapped[float] = mapped_column(Float, default=1.0)
    total_prob: Mapped[float] = mapped_column(Float, default=0.0)
    total_ev: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="coupons")
    selections: Mapped[list["CouponSelection"]] = relationship(back_populates="coupon")


class CouponSelection(Base):
    __tablename__ = "coupon_selections"

    id: Mapped[int] = mapped_column(primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"))

    fixture_id: Mapped[str] = mapped_column(String(64))
    league: Mapped[str] = mapped_column(String(128), default="")
    league_id: Mapped[str] = mapped_column(String(64), default="")
    home: Mapped[str] = mapped_column(String(128), default="")
    away: Mapped[str] = mapped_column(String(128), default="")

    market: Mapped[str] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(128))
    odds: Mapped[float] = mapped_column(Float)
    prob: Mapped[float] = mapped_column(Float)
    ev: Mapped[float] = mapped_column(Float)

    coupon: Mapped["Coupon"] = relationship(back_populates="selections")


class FavoriteLeague(Base):
    __tablename__ = "favorite_leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    league_id: Mapped[str] = mapped_column(String(64))
    league_name: Mapped[str] = mapped_column(String(128), default="")

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class FavoriteTeam(Base):
    __tablename__ = "favorite_teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    team_id: Mapped[str] = mapped_column(String(64))
    team_name: Mapped[str] = mapped_column(String(128), default="")
    league_id: Mapped[str] = mapped_column(String(64), default="")
    league_name: Mapped[str] = mapped_column(String(128), default="")

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class TeamStats(Base):
    __tablename__ = "team_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[str] = mapped_column(String(64), index=True)
    league_name: Mapped[str] = mapped_column(String(128), default="")
    team_name: Mapped[str] = mapped_column(String(128), index=True)
    season: Mapped[str] = mapped_column(String(16), default="2024")

    home_attack: Mapped[float] = mapped_column(Float, default=1.0)
    away_attack: Mapped[float] = mapped_column(Float, default=1.0)
    home_defense: Mapped[float] = mapped_column(Float, default=1.0)
    away_defense: Mapped[float] = mapped_column(Float, default=1.0)
    avg_goals_for: Mapped[float] = mapped_column(Float, default=1.5)
    avg_goals_against: Mapped[float] = mapped_column(Float, default=1.2)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class LiveSnapshotRecord(Base):
    __tablename__ = "live_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str] = mapped_column(String(64), default="manual")
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    predictions: Mapped[list["PredictionSnapshotRecord"]] = relationship(back_populates="snapshot")
    value_bets: Mapped[list["ValueBetSnapshotRecord"]] = relationship(back_populates="snapshot")


class BetJournalEntry(Base):
    __tablename__ = "bet_journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    settled_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)

    fixture_ids: Mapped[list[str]] = mapped_column(JSON, default=_empty_fixture_list)
    league: Mapped[str] = mapped_column(String(128), default="")
    league_id: Mapped[str] = mapped_column(String(64), default="")
    home_team: Mapped[str] = mapped_column(String(128), default="")
    away_team: Mapped[str] = mapped_column(String(128), default="")

    market: Mapped[str] = mapped_column(String(128))
    line: Mapped[Optional[float]] = mapped_column(Float, default=None)
    side: Mapped[str] = mapped_column(String(64))

    odds_at_pick: Mapped[Optional[float]] = mapped_column(Float, default=None)
    model_probability: Mapped[float] = mapped_column(Float)
    fair_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    bookmaker_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    closing_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    clv_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    clv_prob: Mapped[Optional[float]] = mapped_column(Float, default=None)
    snapshot_provider: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    ev: Mapped[float] = mapped_column(Float, default=0.0)
    correlation_risk: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    stake: Mapped[float] = mapped_column(Float, default=1.0)
    stake_rule: Mapped[Optional[str]] = mapped_column(String(64), default=None)

    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending / settled
    result: Mapped[Optional[str]] = mapped_column(String(32), default=None)  # win / loss / void / push / pending
    realized_roi: Mapped[Optional[float]] = mapped_column(Float, default=None)

    meta: Mapped[Optional[dict]] = mapped_column(JSON, default=None)

    user: Mapped[Optional["User"]] = relationship()


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(128), default="workspace")

    status: Mapped[str] = mapped_column(String(32), default="pending")
    params: Mapped[dict] = mapped_column(JSON)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    warnings: Mapped[Optional[list[str]]] = mapped_column(JSON, default=None)
    seed: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)

    user: Mapped[Optional["User"]] = relationship()


class ExecutionOrder(Base):
    __tablename__ = "execution_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    adapter: Mapped[str] = mapped_column(String(64), default="db")
    status: Mapped[str] = mapped_column(String(32), default="queued")

    fixture_id: Mapped[str] = mapped_column(String(64))
    market: Mapped[str] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(128))
    odds: Mapped[float] = mapped_column(Float)
    ev: Mapped[float] = mapped_column(Float)

    meta: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class PredictionSnapshotRecord(Base):
    __tablename__ = "prediction_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("live_snapshots.id"))
    model_version: Mapped[str] = mapped_column(String(64), default="ens_v2.1")
    payload: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    snapshot: Mapped[LiveSnapshotRecord] = relationship(back_populates="predictions")


class ValueBetSnapshotRecord(Base):
    __tablename__ = "value_bet_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("live_snapshots.id"))
    model_version: Mapped[str] = mapped_column(String(64), default="ens_v2.1")
    payload: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    snapshot: Mapped[LiveSnapshotRecord] = relationship(back_populates="value_bets")


class OddsSnapshotRecord(Base):
    __tablename__ = "odds_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[str] = mapped_column(String(64), default="api-football")
    match_id: Mapped[str] = mapped_column(String(64), index=True)
    market_id: Mapped[str] = mapped_column(String(128), index=True)
    selection_id: Mapped[str] = mapped_column(String(64), index=True)
    line: Mapped[Optional[float]] = mapped_column(Float, default=None)
    odds_decimal: Mapped[float] = mapped_column(Float)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    source_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    raw_payload_hash: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    captured_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), index=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="ready")
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    notes: Mapped[Optional[str]] = mapped_column(String(512), default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    activated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)


class ModelArtifact(Base):
    __tablename__ = "model_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), index=True)
    uri: Mapped[str] = mapped_column(String(512))
    checksum: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class ModelActivation(Base):
    __tablename__ = "model_activations"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), index=True)
    previous_version: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    activated_by: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    reason: Mapped[Optional[str]] = mapped_column(String(256), default=None)
    rollback_of: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class FixtureEntity(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(64), default="openfootball-csv")
    league: Mapped[str] = mapped_column(String(128), index=True)
    season: Mapped[str] = mapped_column(String(16))
    home_team: Mapped[str] = mapped_column(String(128))
    away_team: Mapped[str] = mapped_column(String(128))
    kickoff_utc: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    venue: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    results: Mapped[list["ResultEntity"]] = relationship(back_populates="fixture")
    events: Mapped[list["EventEntity"]] = relationship(back_populates="fixture")
    lineups: Mapped[list["LineupEntity"]] = relationship(back_populates="fixture")
    features: Mapped[list["ModelFeatureEntity"]] = relationship(back_populates="fixture")


class ResultEntity(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[str] = mapped_column(ForeignKey("fixtures.fixture_id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), default="openfootball-csv")
    home_score: Mapped[int] = mapped_column(Integer)
    away_score: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="FT")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    fixture: Mapped["FixtureEntity"] = relationship(back_populates="results")


class EventEntity(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[str] = mapped_column(ForeignKey("fixtures.fixture_id"), index=True)
    minute: Mapped[int] = mapped_column(Integer)
    team: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(64))
    player: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    fixture: Mapped["FixtureEntity"] = relationship(back_populates="events")


class LineupEntity(Base):
    __tablename__ = "lineups"

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[str] = mapped_column(ForeignKey("fixtures.fixture_id"), index=True)
    team: Mapped[str] = mapped_column(String(128))
    players: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    fixture: Mapped["FixtureEntity"] = relationship(back_populates="lineups")


class ModelFeatureEntity(Base):
    __tablename__ = "model_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[str] = mapped_column(ForeignKey("fixtures.fixture_id"), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    fixture: Mapped["FixtureEntity"] = relationship(back_populates="features")


class IngestionRunEntity(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=None)
    status: Mapped[str] = mapped_column(String(32), default="started")
    stats: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
