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

    def fit(self, results: Iterable[MatchResult]) -> None:
        leagues: Dict[str, Dict[str, list]] = {}
        for match in results:
            leagues.setdefault(match.league, {}).setdefault(match.home_team, []).append((match.home_goals, match.away_goals))
            leagues.setdefault(match.league, {}).setdefault(match.away_team, []).append((match.away_goals, match.home_goals))

        for league, team_data in leagues.items():
            for team, scores in team_data.items():
                goals_for = [g[0] for g in scores]
                goals_against = [g[1] for g in scores]
                attack = (np.mean(goals_for) + self.league_strength) / (1 + self.league_strength)
                defence = (np.mean(goals_against) + self.league_strength) / (1 + self.league_strength)
                self.team_params[(league, team)] = TeamStrength(attack=attack, defence=defence)

    def strength(self, league: str, team: str) -> TeamStrength:
        """Return team strength, backing off to league priors when absent."""

        key = (league, team)
        if key in self.team_params:
            return self.team_params[key]
        return TeamStrength(attack=1.0, defence=1.0)


