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
    player_rating_diff: float = 0.0
    injury_diff: float = 0.0
    weather_temp_c: float = 0.0
    weather_wind_mps: float = 0.0
    venue_altitude_m: float = 0.0
    live_xg_diff: float = 0.0

    def to_vector(self) -> Dict[str, float]:
        return {
            "home_strength": self.home_strength,
            "away_strength": self.away_strength,
            "form_diff": self.form_diff,
            "rest_diff": self.rest_diff,
            "implied_home": self.implied_home,
            "implied_draw": self.implied_draw,
            "implied_away": self.implied_away,
            "player_rating_diff": self.player_rating_diff,
            "injury_diff": self.injury_diff,
            "weather_temp_c": self.weather_temp_c,
            "weather_wind_mps": self.weather_wind_mps,
            "venue_altitude_m": self.venue_altitude_m,
            "live_xg_diff": self.live_xg_diff,
        }

