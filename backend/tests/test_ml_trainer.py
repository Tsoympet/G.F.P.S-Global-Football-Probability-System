import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend import ml_trainer


def test_run_training_handles_empty_data(monkeypatch, tmp_path):
    db_path = tmp_path / "mltrainer.db"
    engine = create_engine(
        f"sqlite:///{db_path}", future=True, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    models.Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(ml_trainer, "SessionLocal", SessionLocal)

    with SessionLocal() as db:
        run = models.TrainingRun(version="v1", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id

    asyncio.run(ml_trainer._run_training(run_id, "v1"))

    with SessionLocal() as db:
        updated = db.get(models.TrainingRun, run_id)
        assert updated.status == "failed"
        assert updated.completed_at is not None
        assert updated.metrics.get("error") == "No completed fixtures with odds available"
