"""Hierarchical team strength estimation with partial pooling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple
import numpy as np


@dataclass(frozen=True)
class MatchResult:
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    league: str


@dataclass(frozen=True)
class TeamStrength:
    attack: float
    defence: float


class StrengthModel:
    """Simple MAP estimator with league-level priors to stabilize cold starts."""

    def __init__(self, league_strength: float = 0.1, team_precision: float = 1.0) -> None:
        self.league_strength = league_strength
        self.team_precision = team_precision
        self.team_params: Dict[Tuple[str, str], TeamStrength] = {}
        self.league_averages: Dict[str, Tuple[float, float]] = {}

    def fit(self, results: Iterable[MatchResult]) -> None:
        leagues: Dict[str, Dict[str, list]] = {}
        for match in results:
            leagues.setdefault(match.league, {}).setdefault(match.home_team, []).append((match.home_goals, match.away_goals))
            leagues.setdefault(match.league, {}).setdefault(match.away_team, []).append((match.away_goals, match.home_goals))

        for league, team_data in leagues.items():
            goals_for_all = [g[0] for scores in team_data.values() for g in scores]
            goals_against_all = [g[1] for scores in team_data.values() for g in scores]
            league_avg_for = float(np.mean(goals_for_all)) if goals_for_all else 1.0
            league_avg_against = float(np.mean(goals_against_all)) if goals_against_all else 1.0
            self.league_averages[league] = (league_avg_for, league_avg_against)
            for team, scores in team_data.items():
                goals_for = [g[0] for g in scores]
                goals_against = [g[1] for g in scores]
                n = len(scores)
                weight = n * self.team_precision
                prior = max(self.league_strength, 0.0)
                denom = weight + prior
                def shrink(mean_value: float, league_mean: float) -> float:
                    return (mean_value * weight + league_mean * prior) / denom if denom else league_mean
                mean_for = np.mean(goals_for) if goals_for else league_avg_for
                mean_against = np.mean(goals_against) if goals_against else league_avg_against
                shrunk_for = shrink(float(mean_for), league_avg_for)
                shrunk_against = shrink(float(mean_against), league_avg_against)
                attack = shrunk_for / league_avg_for if league_avg_for else 1.0
                defence = shrunk_against / league_avg_against if league_avg_against else 1.0
                self.team_params[(league, team)] = TeamStrength(attack=float(attack), defence=float(defence))

    def strength(self, league: str, team: str) -> TeamStrength:
        """Return team strength, backing off to league priors when absent."""

        key = (league, team)
        if key in self.team_params:
            return self.team_params[key]
        return TeamStrength(attack=1.0, defence=1.0)
