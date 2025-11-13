from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    role: Mapped[str] = mapped_column(String(32), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # token version – if incremented, old JWTs become invalid
    token_version: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

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
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(32))  # android / ios / web
    token: Mapped[str] = mapped_column(String(512))
    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="devices")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))

    league_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    team_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    market_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    outcome_filter: Mapped[Optional[str]] = mapped_column(String(128), default=None)

    min_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    max_odds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    min_ev: Mapped[Optional[float]] = mapped_column(Float, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

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

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

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

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

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

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())


class FavoriteTeam(Base):
    __tablename__ = "favorite_teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    team_id: Mapped[str] = mapped_column(String(64))
    team_name: Mapped[str] = mapped_column(String(128), default="")
    league_id: Mapped[str] = mapped_column(String(64), default="")
    league_name: Mapped[str] = mapped_column(String(128), default="")

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="")

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="room")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("chat_rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())

    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship(back_populates="chat_messages")


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

    created_at: Mapped = mapped_column(DateTime, server_default=func.now())
