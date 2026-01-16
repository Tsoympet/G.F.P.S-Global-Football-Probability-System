from __future__ import annotations

from typing import List, Dict

ValuePreset = Dict[str, object]


def _base_presets() -> List[ValuePreset]:
    return [
        {
            "id": "premier-league-ev-medium",
            "label": "Premier League | EV ≥ 5%",
            "leagues": ["Premier League"],
            "markets": ["Match Winner", "Over/Under"],
            "minEv": 0.05,
        },
        {
            "id": "la-liga-ev-high",
            "label": "La Liga | EV ≥ 8%",
            "leagues": ["La Liga"],
            "markets": ["Match Winner"],
            "minEv": 0.08,
        },
        {
            "id": "btts-europe",
            "label": "BTTS Europe | EV ≥ 4%",
            "leagues": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"],
            "markets": ["Both Teams To Score"],
            "minEv": 0.04,
        },
    ]


def get_value_presets() -> List[ValuePreset]:
    return _base_presets()
