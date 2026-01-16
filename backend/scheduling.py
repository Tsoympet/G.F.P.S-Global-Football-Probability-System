from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Callable, Coroutine

from .ingestion_pipeline import build_features, ingest_fixtures, ingest_live


async def _run_with_backoff(task: Callable[[], Coroutine], base_delay: float = 1.0, retries: int = 3):
    delay = base_delay
    for attempt in range(retries):
        try:
            await task()
            return
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2


async def schedule_daily_fixtures():
    async def _task():
        ingest_fixtures()
    while True:
        await _run_with_backoff(_task)
        await asyncio.sleep(timedelta(days=1).total_seconds())


async def schedule_live_refresh():
    async def _task():
        ingest_live()
    while True:
        await _run_with_backoff(_task, base_delay=2.0)
        await asyncio.sleep(120)


async def schedule_feature_build():
    async def _task():
        build_features()
    while True:
        await _run_with_backoff(_task, base_delay=2.0)
        await asyncio.sleep(timedelta(hours=6).total_seconds())
