from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


def parse_utc_datetime(value: Optional[str], default_future: bool = False) -> datetime:
    """Parse an ISO timestamp (with optional 'Z') into UTC."""
    if value:
        try:
            cleaned = value.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned).astimezone(timezone.utc)
        except ValueError:
            pass
    fallback = datetime.now(timezone.utc)
    if default_future:
        fallback = fallback + timedelta(days=1)
    return fallback
