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


def parse_iso_datetime(value: str) -> str:
    if not value:
        raise ValueError("Missing datetime value")
    try:
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid datetime value: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


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
