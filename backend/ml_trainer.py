"""Toy training scheduler that persists model versions and metrics."""

from __future__ import annotations

import asyncio
import random
from datetime import datetime

from .db import SessionLocal
from .models import ModelVersion, TrainingRun


async def _simulate_training(run_id: int, version: str) -> None:
    await asyncio.sleep(1)  # placeholder for real training workload

    metrics = {
        "logLoss": round(random.uniform(0.45, 0.65), 3),
        "roi": round(random.uniform(0.02, 0.08), 3),
        "samples": random.randint(5000, 10000),
    }

    with SessionLocal() as db:
        run = db.get(TrainingRun, run_id)
        if run:
            run.status = "completed"
            run.metrics = metrics
            run.completed_at = datetime.utcnow()
            db.add(run)

        model = db.query(ModelVersion).filter(ModelVersion.version == version).first()
        if not model:
            model = ModelVersion(version=version, status="ready", metrics=metrics)
        else:
            model.metrics = metrics
            model.status = "ready"
        db.add(model)
        db.commit()


def queue_training(loop: asyncio.AbstractEventLoop, version: str) -> int:
    with SessionLocal() as db:
        run = TrainingRun(version=version, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

    loop.create_task(_simulate_training(run.id, version))
    return run.id
