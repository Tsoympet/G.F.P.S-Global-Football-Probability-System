"""
In-memory live state store for fixtures, events, and odds snapshots.

This module offers a tiny publisher/subscriber mechanism used by the
HTTP endpoints and the `/ws/live-matches` WebSocket to share the same
snapshot data without requiring a real cache or database.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, List

_DEMO_START = datetime.utcnow().replace(microsecond=0)


class LiveState:
    def __init__(self) -> None:
        # Default demo fixtures
        self.fixtures: List[Dict[str, Any]] = [
            {
                "id": "1",
                "league": "Premier League",
                "homeTeam": "Demo FC",
                "awayTeam": "Sample United",
                "startTime": (_DEMO_START + timedelta(hours=1)).isoformat() + "Z",
                "status": "scheduled",
            },
            {
                "id": "2",
                "league": "La Liga",
                "homeTeam": "Example Town",
                "awayTeam": "Placeholder City",
                "startTime": (_DEMO_START + timedelta(hours=2)).isoformat() + "Z",
                "status": "scheduled",
            },
        ]
        self.events: List[Dict[str, Any]] = []
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    def snapshot(self) -> Dict[str, Any]:
        return {"fixtures": deepcopy(self.fixtures), "events": deepcopy(self.events)}

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue) -> None:
        async with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    async def broadcast(self, payload: Dict[str, Any] | None = None) -> None:
        if payload is None:
            payload = self.snapshot()
        async with self._lock:
            for q in list(self._subscribers):
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    # drop message for that subscriber to avoid blocking
                    pass

    async def set_fixtures(self, fixtures: List[Dict[str, Any]]) -> None:
        self.fixtures = deepcopy(fixtures)
        await self.broadcast({"type": "fixtures", **self.snapshot()})

    async def add_event(self, event: Dict[str, Any]) -> None:
        self.events.append(event)
        await self.broadcast({"type": "event", "event": deepcopy(event), **self.snapshot()})

    async def tick_demo_clock(self) -> None:
        """Simulate a minimal live update for demo fixtures."""
        if not self.fixtures:
            return
        f = self.fixtures[0]
        if f.get("status") == "scheduled":
            f["status"] = "live"
            f["timer"] = "1'"
            f["score"] = {"home": 0, "away": 0}
            await self.broadcast({"type": "kickoff", **self.snapshot()})
            return

        if f.get("status") == "live":
            # increment timer minute up to 90 then mark finished
            current_minute = 1
            timer = f.get("timer")
            if isinstance(timer, str) and timer.endswith("'"):
                try:
                    current_minute = int(timer[:-1])
                except ValueError:
                    current_minute = 1
            new_minute = current_minute + 1
            if new_minute >= 90:
                f["status"] = "finished"
                f["timer"] = None
                await self.broadcast({"type": "fulltime", **self.snapshot()})
            else:
                f["timer"] = f"{new_minute}'"
                await self.broadcast({"type": "heartbeat", **self.snapshot()})


live_state = LiveState()
