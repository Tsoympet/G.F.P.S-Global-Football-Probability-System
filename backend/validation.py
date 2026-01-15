from __future__ import annotations

from datetime import date, datetime, timezone
import math
from typing import Optional


def parse_date_string(value: Optional[str]) -> str:
    if not value:
        return date.today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"Invalid date format: {value}") from exc


def _normalize_to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_iso_datetime(value: str) -> str:
    if not value:
        raise ValueError("Missing datetime value")
    try:
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid datetime value: {value}") from exc
    return _normalize_to_utc(parsed).isoformat().replace("+00:00", "Z")


def format_iso_datetime(value: Optional[datetime]) -> Optional[str]:
    if not value:
        return None
    return _normalize_to_utc(value).isoformat().replace("+00:00", "Z")


def validate_odds_bounds(min_odds: Optional[float], max_odds: Optional[float]) -> None:
    if min_odds is not None and max_odds is not None and min_odds > max_odds:
        raise ValueError("min_odds cannot exceed max_odds")


def require_decimal_odds(value: float, label: str) -> float:
    if value is None or not math.isfinite(value) or value <= 1.0:
        raise ValueError(f"Invalid decimal odds for {label}: {value}")
    return float(value)


def parse_market_line(value: str) -> float:
    try:
        line = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid market line: {value}") from exc
    if not math.isfinite(line) or line <= 0:
        raise ValueError(f"Invalid market line: {value}")
    return line
