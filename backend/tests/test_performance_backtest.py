from datetime import datetime, timedelta, timezone
from math import isclose

from backend.models import BetJournalEntry
from backend.performance_tracking import (
    BacktestRules,
    BacktestSnapshot,
    JournalRow,
    compute_performance_kpis,
    run_backtest,
    settle_entry,
)


def test_roi_yield_and_hit_rate():
    now = datetime.now(timezone.utc)
    rows = [
        JournalRow(
            stake=100,
            ev=0.08,
            result="win",
            realized_roi=0.5,
            market="1x2",
            league="Test",
            home_team="A",
            away_team="B",
            created_at=now - timedelta(days=1),
            side="home",
            bookmaker_odds=2.0,
        ),
        JournalRow(
            stake=50,
            ev=0.04,
            result="loss",
            realized_roi=-1.0,
            market="1x2",
            league="Test",
            home_team="C",
            away_team="D",
            created_at=now,
            side="away",
            bookmaker_odds=1.8,
        ),
    ]
    kpis = compute_performance_kpis(rows)
    assert kpis["totalBets"] == 2
    assert kpis["wins"] == 1
    assert kpis["losses"] == 1
    assert kpis["hitRate"] == 0.5
    assert kpis["roi"] == 0.0  # +50 pnl -50 pnl / 150 stake
    assert kpis["yield"] == 0.0


def test_settlement_logic_and_drawdown():
    entry = BetJournalEntry(
        stake=25,
        market="1x2",
        side="home",
        model_probability=0.55,
        ev=0.1,
        correlation_risk=0.0,
        confidence=0.7,
        league="Test",
        home_team="A",
        away_team="B",
        fair_odds=2.0,
    )
    settle_entry(entry, "home", closing_odds=2.2)
    assert entry.result == "win"
    assert isclose(entry.realized_roi, 1.2, rel_tol=1e-9)
    entry2 = BetJournalEntry(
        stake=25,
        market="1x2",
        side="home",
        model_probability=0.55,
        ev=0.1,
        correlation_risk=0.0,
        confidence=0.7,
        league="Test",
        home_team="A",
        away_team="B",
        fair_odds=2.0,
    )
    settle_entry(entry2, "away", closing_odds=2.2)
    row_win = JournalRow(
        stake=entry.stake,
        ev=entry.ev,
        result=entry.result,
        realized_roi=entry.realized_roi,
        market=entry.market,
        league=entry.league,
        home_team=entry.home_team,
        away_team=entry.away_team,
        created_at=datetime.now(timezone.utc) - timedelta(days=2),
        side=entry.side,
        bookmaker_odds=entry.bookmaker_odds,
    )
    row_loss = JournalRow(
        stake=entry2.stake,
        ev=entry2.ev,
        result=entry2.result,
        realized_roi=entry2.realized_roi,
        market=entry2.market,
        league=entry2.league,
        home_team=entry2.home_team,
        away_team=entry2.away_team,
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
        side=entry2.side,
        bookmaker_odds=entry2.bookmaker_odds,
    )
    kpis = compute_performance_kpis([row_win, row_loss])
    assert kpis["maxDrawdown"] == 25.0  # equity from +30 to -25
    assert kpis["currentDrawdown"] == 25.0


def _basic_snapshot(ts: datetime, prob: float = 0.55, odds: float = 2.0):
    return BacktestSnapshot(
        timestamp=ts,
        fixtures=[
            {
                "id": "fx1",
                "league": "Test League",
                "homeTeam": "A",
                "awayTeam": "B",
                "startTime": ts.isoformat(),
            }
        ],
        predictions=[
            {
                "fixtureId": "fx1",
                "homeWinProbability": prob,
                "drawProbability": 0.2,
                "awayWinProbability": 1 - prob - 0.2,
                "finalOdds": {"home": odds, "draw": 3.5, "away": 3.4},
                "confidence": 0.8,
            }
        ],
        odds_by_fixture={"fx1": {"home": odds, "draw": 3.5, "away": 3.4}},
    )


def test_backtest_determinism_and_rules():
    ts = datetime.now(timezone.utc)
    snapshot = _basic_snapshot(ts)
    results = {"fx1": {"outcome": "home", "timestamp": ts + timedelta(hours=2)}}
    rules = BacktestRules(markets=["1x2"], min_ev=0.01, min_confidence=0.1, max_per_day=2, exclude_correlated_above=0.5)
    first = run_backtest([snapshot], results, rules, seed=42)
    second = run_backtest([snapshot], results, rules, seed=42)
    assert first["roi"] == second["roi"]
    assert first["sampleSize"] == 1
    assert first["hitRate"] == 1.0


def test_anti_lookahead_skips_finished_snapshot():
    ts = datetime.now(timezone.utc)
    snapshot = _basic_snapshot(ts)
    results = {"fx1": {"outcome": "home", "timestamp": ts - timedelta(hours=1)}}
    rules = BacktestRules(markets=["1x2"], min_ev=-1.0, min_confidence=0.0, max_per_day=5, exclude_correlated_above=0.5)
    metrics = run_backtest([snapshot], results, rules, seed=1, enforce_anti_lookahead=True)
    assert metrics["sampleSize"] == 0
    assert metrics["roi"] == 0.0


def test_rule_filters_ev_and_correlation():
    ts = datetime.now(timezone.utc)
    snapshot = BacktestSnapshot(
        timestamp=ts,
        fixtures=[
            {"id": "fx1", "league": "Test League", "homeTeam": "A", "awayTeam": "B", "startTime": ts.isoformat()}
        ],
        predictions=[
            {
                "fixtureId": "fx1",
                "homeWinProbability": 0.6,
                "drawProbability": 0.2,
                "awayWinProbability": 0.2,
                "finalOdds": {"home": 1.9, "draw": 3.4, "away": 5.0},
                "confidence": 0.6,
            },
            {
                "fixtureId": "fx1",
                "homeWinProbability": 0.2,
                "drawProbability": 0.2,
                "awayWinProbability": 0.6,
                "finalOdds": {"home": 5.0, "draw": 3.4, "away": 1.9},
                "confidence": 0.6,
            },
        ],
        odds_by_fixture={"fx1": {"home": 1.9, "draw": 3.4, "away": 1.9}},
    )
    results = {"fx1": {"outcome": "home", "timestamp": ts + timedelta(hours=2)}}
    rules = BacktestRules(
        markets=["1x2"],
        min_ev=0.05,
        min_confidence=0.5,
        max_per_day=5,
        exclude_correlated_above=0.0,
    )
    metrics = run_backtest([snapshot], results, rules, seed=0)
    # Only one side should be taken due to correlation filter and EV threshold
    assert metrics["sampleSize"] == 1
    assert metrics["roi"] != 0.0
