"""
In-memory live state store for fixtures, events, and odds snapshots.

This module offers a tiny publisher/subscriber mechanism used by the HTTP
endpoints and the `/ws/live-matches` WebSocket to share the same snapshot data
without requiring a real cache or database.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

_SEED_START = datetime.now(timezone.utc).replace(microsecond=0)


class LiveState:
    def __init__(self) -> None:
        # Seed fixtures used when no upstream data is available.
        self.fixtures: List[Dict[str, Any]] = [
            {
                "id": "1",
                "league": "Premier League",
                "leagueId": "39",
                "homeTeam": "Northbridge FC",
                "awayTeam": "Harbor United",
                "startTime": (_SEED_START + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": "scheduled",
            },
            {
                "id": "2",
                "league": "La Liga",
                "leagueId": "140",
                "homeTeam": "Valencia Norte",
                "awayTeam": "Costa Azul",
                "startTime": (_SEED_START + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": "scheduled",
            },
        ]
        self.events: Dict[str, List[Dict[str, Any]]] = {}
        self.odds: List[Dict[str, Any]] = []
        self._odds_index: Dict[str, int] = {}
        self.market_lines: Dict[str, List[Dict[str, Any]]] = {}
        self.event_feed: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "fixtures": deepcopy(self.fixtures),
            "events": deepcopy(self.events),
            "eventFeed": deepcopy(self.event_feed),
            "odds": deepcopy(self.odds),
            "markets": deepcopy(self.market_lines),
        }

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
        await self._persist_snapshot("fixtures_update")

    async def set_odds(self, odds: List[Dict[str, Any]]) -> None:
        self.odds = deepcopy(odds)
        self._odds_index = {
            str(row.get("fixtureId") or row.get("fixture_id") or ""): idx for idx, row in enumerate(self.odds)
        }
        await self.broadcast({"type": "odds", **self.snapshot()})
        await self._persist_snapshot("odds_update")

    async def apply_odds_delta(self, odds_delta: Dict[str, Any]) -> None:
        """
        Apply a partial odds update for a single fixture without replacing the entire book.
        """
        fixture_id = str(odds_delta.get("fixtureId") or odds_delta.get("fixture_id") or "")
        if not fixture_id:
            return
        idx = self._odds_index.get(fixture_id)
        if idx is not None and 0 <= idx < len(self.odds):
            self.odds[idx].update(odds_delta)
        else:
            payload = {"fixtureId": fixture_id}
            payload.update(odds_delta)
            self.odds.append(payload)
            self._odds_index[fixture_id] = len(self.odds) - 1
            idx = self._odds_index[fixture_id]
        snapshot_odds = deepcopy(self.odds[idx]) if idx is not None and 0 <= idx < len(self.odds) else None
        payload = {"type": "odds_delta", "fixtureId": fixture_id}
        if snapshot_odds is not None:
            payload["odds"] = snapshot_odds
        await self.broadcast(payload)
        await self._persist_snapshot("odds_delta")

    async def set_markets(self, markets: Dict[str, List[Dict[str, Any]]]) -> None:
        self.market_lines = deepcopy(markets)
        await self.broadcast({"type": "markets", **self.snapshot()})
        await self._persist_snapshot("markets_update")

    async def set_events(self, events: Dict[str, List[Dict[str, Any]]]) -> None:
        self.events = deepcopy(events)
        self.event_feed = self._build_event_feed(events)
        await self.broadcast({"type": "events", **self.snapshot()})
        await self._persist_snapshot("events_update")

    async def add_event(self, fixture_id: str, event: Dict[str, Any]) -> None:
        if fixture_id not in self.events:
            self.events[fixture_id] = []
        self.events[fixture_id].append(event)
        self._insert_event_into_feed(fixture_id, event)
        await self.broadcast(
            {"type": "event", "fixtureId": fixture_id, "event": deepcopy(event), **self.snapshot()}
        )
        await self._persist_snapshot("event")

    async def tick_fallback_clock(self) -> None:
        """Simulate a minimal live update for seeded fixtures."""
        if not self.fixtures:
            return
        f = self.fixtures[0]
        if f.get("status") == "scheduled":
            f["status"] = "live"
            f["timer"] = "1'"
            f["score"] = {"home": 0, "away": 0}
            await self.add_event(
                f.get("id", "seed"),
                {"minute": 1, "description": "Kick-off", "type": "info"},
            )
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

    async def _persist_snapshot(self, reason: str) -> None:
        try:
            from .snapshot_service import capture_snapshot

            await capture_snapshot(reason=reason)
        except Exception as exc:  # pragma: no cover - best effort
            print(f"[live_state] persist failed: {exc}")

    def _build_event_feed(
        self, events: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        feed: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for fixture_id, rows in (events or {}).items():
            for ev in rows or []:
                self._insert_event_into_feed(fixture_id, ev, feed)
        return feed

    def _insert_event_into_feed(
        self,
        fixture_id: str,
        event: Dict[str, Any],
        feed: Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]] = None,
    ) -> None:
        target = feed if feed is not None else self.event_feed
        bucket = target.setdefault(
            fixture_id,
            {"cards": [], "corners": [], "substitutions": [], "other": []},
        )
        category = (event.get("type") or "").lower()
        normalized = dict(event)
        if category in {"red card", "yellow card", "card"} or "card" in category:
            bucket["cards"].append(normalized)
        elif "corner" in category:
            bucket["corners"].append(normalized)
        elif "substitution" in category or category in {"sub", "subs"}:
            bucket["substitutions"].append(normalized)
        else:
            bucket["other"].append(normalized)


live_state = LiveState()
