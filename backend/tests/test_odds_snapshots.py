from datetime import datetime, timedelta, timezone

import pytest

from backend.db import Base, SessionLocal, engine
from backend.models import OddsSnapshotRecord
from backend.odds_snapshot_pipeline import closing_odds, record_odds_snapshots
from backend.evaluation.clv import beat_closing_line, clv_odds_space, clv_probability_space


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_snapshot_deduplication_and_ordering():
    now = datetime.now(timezone.utc)
    row = {"fixtureId": "m1", "market": "1x2", "home": 2.1, "draw": 3.4, "away": 3.3}
    inserted = record_odds_snapshots([row], captured_at=now)
    assert inserted == 3  # one per selection
    inserted_dup = record_odds_snapshots([row], captured_at=now + timedelta(seconds=10))
    assert inserted_dup == 0  # deduped within window
    # ensure only three rows exist
    with SessionLocal() as db:
        assert db.query(OddsSnapshotRecord).count() == 3


def test_closing_odds_selection_and_clv_math():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    kickoff = datetime.now(timezone.utc)
    early = {"fixtureId": "m2", "market": "1x2", "home": 2.2, "draw": 3.5, "away": 3.1}
    late = {"fixtureId": "m2", "market": "1x2", "home": 2.0, "draw": 3.4, "away": 3.0}
    record_odds_snapshots([early], captured_at=kickoff - timedelta(minutes=30))
    record_odds_snapshots([late], captured_at=kickoff + timedelta(minutes=5))
    close_price = closing_odds("m2", "1x2", "home", kickoff)
    assert close_price == 2.2  # uses last price before kickoff
    clv_odds = clv_odds_space(2.4, close_price)
    clv_prob = clv_probability_space(2.4, close_price)
    assert clv_odds == pytest.approx((2.4 / close_price) - 1)
    assert clv_prob == pytest.approx((1 / close_price) - (1 / 2.4))
    assert beat_closing_line(2.4, close_price) is True
