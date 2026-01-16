from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TTLCache:
    """Very small JSON-backed cache with TTL and fallback to last known good."""

    def __init__(self, path: Optional[Path] = None, ttl_seconds: int = 900, fallback_to_last_good: bool = True) -> None:
        self.path = path or Path(".cache/gfps-cache.json")
        self.ttl_seconds = ttl_seconds
        self.fallback_to_last_good = fallback_to_last_good
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            logger.warning("Cache file %s is corrupted; ignoring cache", self.path)
            return None
        entry = data.get(key)
        if not entry:
            return None
        if time.time() - entry.get("ts", 0) > self.ttl_seconds:
            return entry.get("last_good") if self.fallback_to_last_good else None
        return entry.get("value")

    def set(self, key: str, value: Any) -> None:
        data = {}
        previous_entry = None
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    previous_entry = data.get(key)
            except json.JSONDecodeError:
                logger.warning("Cache file %s is corrupted; resetting entry %s", self.path, key)
                data = {}
        last_good = None
        if previous_entry:
            last_good = previous_entry.get("last_good", previous_entry.get("value"))
        payload = {"value": value, "ts": time.time(), "last_good": last_good or value}
        data[key] = payload
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle)
