"""Feature schema for 1X2 classifier."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MatchFeatures:
    fixture_id: str
    league: str
    home_team: str
    away_team: str
    home_strength: float
    away_strength: float
    form_diff: float
    rest_diff: float
    implied_home: float
    implied_draw: float
    implied_away: float

    def to_vector(self) -> Dict[str, float]:
        return {
            "home_strength": self.home_strength,
            "away_strength": self.away_strength,
            "form_diff": self.form_diff,
            "rest_diff": self.rest_diff,
            "implied_home": self.implied_home,
            "implied_draw": self.implied_draw,
            "implied_away": self.implied_away,
        }


