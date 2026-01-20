from datetime import datetime
import unittest

from backend.web_scraper_engine import run_web_scraper_engine
from backend.data_providers.web_scraper import WebScraperProvider
from backend.data_providers.base import EventRecord, FixtureRecord, LineupRecord, OddsRecord


class StubScraper(WebScraperProvider):
    def __init__(self):
        super().__init__(allow_network=False, config={"selectors": {"fixture_container": ".match"}})

    def get_fixtures(self):
        return [
            FixtureRecord(
                fixture_id="fx1",
                league="Test League",
                season="2024",
                home_team="Home",
                away_team="Away",
                kickoff=datetime(2024, 1, 1, 12, 0),
                venue=None,
                timezone="UTC",
            )
        ]

    def get_results(self):
        return []

    def get_odds(self):
        return [
            OddsRecord(fixture_id="fx1", market="1x2", outcome="home", odds=2.0),
            OddsRecord(fixture_id="fx1", market="1x2", outcome="draw", odds=3.4),
            OddsRecord(fixture_id="fx1", market="1x2", outcome="away", odds=4.1),
        ]

    def get_live_events(self):
        return [
            EventRecord(fixture_id="fx1", minute=12, team="Home", type="goal", player="Player A"),
        ]

    def get_lineups(self):
        return [
            LineupRecord(fixture_id="fx1", team="Home", players=["Player A", "Player B"]),
            LineupRecord(fixture_id="fx1", team="Away", players=["Player C", "Player D"]),
        ]


class WebScraperEngineTests(unittest.TestCase):
    def test_run_engine_returns_predictions(self):
        stub = StubScraper()
        payload = run_web_scraper_engine(provider=stub)
        self.assertEqual(len(payload), 1)
        prediction = payload[0]["predictions"]
        self.assertIn("probabilities", prediction)
        self.assertIn("home", prediction["probabilities"])
        self.assertEqual(len(payload[0]["events"]), 1)
        self.assertEqual(len(payload[0]["lineups"]), 2)


if __name__ == "__main__":
    unittest.main()
