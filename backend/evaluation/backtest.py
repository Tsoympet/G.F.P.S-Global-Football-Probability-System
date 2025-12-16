"""Simple portfolio backtester for 1X2 strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping
import numpy as np


@dataclass(frozen=True)
class Bet:
    outcome: str
    probability: float
    odds: float
    stake: float
    result: str


def run_backtest(bets: Iterable[Bet]) -> Mapping[str, float]:
    stakes, pnl = [], []
    for bet in bets:
        stakes.append(bet.stake)
        if bet.outcome == bet.result:
            pnl.append(bet.stake * (bet.odds - 1))
        else:
            pnl.append(-bet.stake)
    total_stake = float(np.sum(stakes)) if stakes else 0.0
    total_pnl = float(np.sum(pnl)) if pnl else 0.0
    roi = total_pnl / total_stake if total_stake else 0.0
    max_drawdown = 0.0
    equity = 0.0
    peak = 0.0
    for change in pnl:
        equity += change
        peak = max(peak, equity)
        drawdown = peak - equity
        max_drawdown = max(max_drawdown, drawdown)
    return {"pnl": total_pnl, "roi": roi, "max_drawdown": max_drawdown}


