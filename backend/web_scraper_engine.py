from __future__ import annotations

import argparse
import json
from typing import Dict, Iterable, List, Optional

from backend.data_providers import WebScraperProvider, load_settings_from_env
from backend.data_providers.base import OddsRecord
from backend.prediction_engine.engine import PredictionEngine, PredictionInput


def _odds_by_fixture(odds: Optional[Iterable[OddsRecord]]) -> Dict[str, Dict[str, float]]:
    odds_map: Dict[str, Dict[str, float]] = {}
    if not odds:
        return odds_map
    for record in odds:
        if getattr(record, "market", "") not in {"1x2", "1X2", "match_winner", "home_draw_away"}:
            continue
        fixture_odds = odds_map.setdefault(record.fixture_id, {})
        outcome = record.outcome.lower()
        if outcome in {"home", "draw", "away"}:
            fixture_odds[outcome] = record.odds
    return odds_map


def _build_prediction_inputs(fixtures, odds_map: Dict[str, Dict[str, float]]) -> Iterable[PredictionInput]:
    for fixture in fixtures:
        yield PredictionInput(
            fixture_id=fixture.fixture_id,
            league=fixture.league,
            home_team=fixture.home_team,
            away_team=fixture.away_team,
            odds=odds_map.get(fixture.fixture_id, {}),
            recent_results=[],
        )


def run_web_scraper_engine(provider: Optional[WebScraperProvider] = None) -> List[dict]:
    if provider is None:
        settings = load_settings_from_env()
        provider = WebScraperProvider(allow_network=settings.live_network_enabled)

    fixtures = list(provider.get_fixtures() or [])
    results = list(provider.get_results() or [])
    odds_iter = provider.get_odds() if hasattr(provider, "get_odds") else None
    odds_map = _odds_by_fixture(odds_iter or None)

    engine = PredictionEngine()
    payload = []

    results_by_fixture = {r.fixture_id: r for r in results}

    for fixture, prediction_input in zip(fixtures, _build_prediction_inputs(fixtures, odds_map)):
        prediction = engine.predict(prediction_input)
        payload.append(
            {
                "fixture_id": fixture.fixture_id,
                "league": fixture.league,
                "home_team": fixture.home_team,
                "away_team": fixture.away_team,
                "kickoff": fixture.kickoff,
                "predictions": prediction,
                "result": results_by_fixture.get(fixture.fixture_id),
            }
        )

    return payload


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run web scraper-powered prediction engine")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command in (None, "run"):
        result = run_web_scraper_engine()
    else:
        raise SystemExit(1)

    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
