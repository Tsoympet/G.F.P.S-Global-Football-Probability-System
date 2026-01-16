from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional


class TTLCache:
    """Very small JSON-backed cache with TTL and fallback to last known good."""

    def __init__(self, path: Optional[Path] = None, ttl_seconds: int = 900) -> None:
        self.path = path or Path(".cache/gfps-cache.json")
        self.ttl_seconds = ttl_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            return None
        entry = data.get(key)
        if not entry:
            return None
        if time.time() - entry.get("ts", 0) > self.ttl_seconds:
            return entry.get("last_good")
        return entry.get("value")

    def set(self, key: str, value: Any) -> None:
        payload = {"value": value, "ts": time.time(), "last_good": value}
        data = {}
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except json.JSONDecodeError:
                data = {}
        data[key] = payload
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle)
