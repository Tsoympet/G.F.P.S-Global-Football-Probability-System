from __future__ import annotations

from typing import Dict, List


def _market_label(home: str | None, away: str | None) -> str:
    return f"{home or 'Home'} vs {away or 'Away'}"


def implied_probabilities(odds: Dict[str, float]) -> Dict[str, float]:
    """Convert decimal odds into normalized implied probabilities.

    This is a lightweight utility used to backfill predictions from odds when
    no model output exists. We strip out the vig by normalizing the inverse
    prices.
    """

    inverse_sum = 0.0
    implied: Dict[str, float] = {}
    for key in ("home", "draw", "away"):
        price = odds.get(key)
        if not price:
            continue
        implied[key] = 1 / price
        inverse_sum += implied[key]

    if inverse_sum == 0:
        return {}

    return {outcome: round(prob / inverse_sum, 4) for outcome, prob in implied.items()}


def generate_predictions(snapshot: Dict[str, List[Dict]]) -> List[Dict]:
    """Return desktop-shaped predictions derived from odds or demo defaults."""

    odds_lookup: Dict[str, Dict[str, float]] = {}
    for o in snapshot.get("odds", []) or []:
        odds_lookup[o.get("market") or ""] = {
            "home": o.get("home"),
            "draw": o.get("draw"),
            "away": o.get("away"),
        }

    predictions: List[Dict] = []
    for fx in snapshot.get("fixtures", []) or []:
        label = _market_label(fx.get("homeTeam"), fx.get("awayTeam"))
        implied = implied_probabilities(odds_lookup.get(label, {}))

        home = implied.get("home", 0.45)
        draw = implied.get("draw", 0.28)
        away = implied.get("away", 0.27)

        # Re-normalize in case demo defaults are mixed with partial odds
        total = home + draw + away
        if total == 0:
            home, draw, away = 0.45, 0.28, 0.27
        else:
            home, draw, away = home / total, draw / total, away / total

        predictions.append(
            {
                "fixtureId": fx.get("id"),
                "homeWinProbability": round(home, 3),
                "drawProbability": round(draw, 3),
                "awayWinProbability": round(away, 3),
            }
        )

    return predictions


def compute_value_bets(snapshot: Dict[str, List[Dict]]) -> List[Dict]:
    """Join model probabilities with latest odds to derive EV rows."""

    odds_lookup: Dict[str, Dict[str, float]] = {}
    for row in snapshot.get("odds", []) or []:
        odds_lookup[row.get("market") or ""] = row

    predictions = generate_predictions(snapshot)
    value_bets: List[Dict] = []

    for pred in predictions:
        fx_id = pred.get("fixtureId")
        fx = next((f for f in snapshot.get("fixtures", []) if f.get("id") == fx_id), None)
        if not fx:
            continue

        label = _market_label(fx.get("homeTeam"), fx.get("awayTeam"))
        odds = odds_lookup.get(label)
        if not odds:
            # Keep a demo-friendly row even when odds are missing
            odds = {"home": 2.0, "draw": 3.2, "away": 3.8, "market": label}

        for outcome, prob_key in (
            ("home", "homeWinProbability"),
            ("draw", "drawProbability"),
            ("away", "awayWinProbability"),
        ):
            price = odds.get(outcome)
            if not price:
                continue
            model_prob = pred.get(prob_key) or 0
            ev = model_prob * price - 1
            value_bets.append(
                {
                    "match": label,
                    "market": f"Match Winner - {outcome.title()}",
                    "odds": price,
                    "modelProbability": round(model_prob, 3),
                    "expectedValue": round(ev, 3),
                }
            )

    return value_bets
