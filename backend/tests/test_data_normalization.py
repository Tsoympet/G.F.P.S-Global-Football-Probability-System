import unittest
from datetime import datetime, timezone

from backend.data_normalization import (
    normalize_fixture,
    normalize_league,
    normalize_team_name,
    normalize_timezone,
    stable_fixture_id,
)
from backend.data_providers.base import FixtureRecord


class NormalizationTests(unittest.TestCase):
    def test_team_alias(self):
        self.assertEqual(normalize_team_name("man utd"), "Manchester United")

    def test_league_alias(self):
        self.assertEqual(normalize_league("EPL"), "Premier League")

    def test_timezone_normalization(self):
        dt = datetime(2024, 1, 1, 12, 0)
        normalized = normalize_timezone(dt)
        self.assertEqual(normalized.tzinfo, timezone.utc)

    def test_stable_id(self):
        rec = FixtureRecord(
            fixture_id="",
            league="EPL",
            season="2024",
            home_team="Man Utd",
            away_team="Liverpool",
            kickoff=datetime(2024, 8, 10, 15, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(len(stable_fixture_id(rec)), 12)

    def test_normalize_fixture_sets_id(self):
        rec = FixtureRecord(
            fixture_id="",
            league="EPL",
            season="2024",
            home_team="Spurs",
            away_team="Man City",
            kickoff=datetime(2024, 8, 10, 15, 30, tzinfo=timezone.utc),
        )
        normalized = normalize_fixture(rec)
        self.assertTrue(normalized.fixture_id)


if __name__ == "__main__":
    unittest.main()
