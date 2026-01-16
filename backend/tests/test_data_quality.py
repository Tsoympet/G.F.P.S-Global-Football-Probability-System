import unittest
from datetime import datetime, timedelta, timezone

from backend.data_quality import confidence_score, deduplicate_records, detect_anomalies
from backend.data_providers.base import ResultRecord


class QualityTests(unittest.TestCase):
    def test_anomaly_detection(self):
        rec = ResultRecord(
            fixture_id="A",
            league="Premier League",
            season="2024",
            home_team="Arsenal",
            away_team="Chelsea",
            kickoff=datetime.now(timezone.utc) + timedelta(days=1),
            home_score=1,
            away_score=0,
        )
        self.assertIn("kickoff_in_future_for_result", detect_anomalies(rec))

    def test_dedup_prefers_confidence(self):
        rec_a = ResultRecord(
            fixture_id="A",
            league="Premier League",
            season="2024",
            home_team="Arsenal",
            away_team="Chelsea",
            kickoff=datetime.now(timezone.utc),
            home_score=1,
            away_score=0,
        )
        rec_b = ResultRecord(
            fixture_id="A",
            league="Premier League",
            season="2024",
            home_team="Arsenal",
            away_team="Chelsea",
            kickoff=datetime.now(timezone.utc),
            home_score=2,
            away_score=0,
        )

        deduped = deduplicate_records(
            [rec_a, rec_b],
            key_func=lambda r: r.fixture_id,
            confidence_func=lambda r: confidence_score(r, source_priority=2 if r.home_score == 2 else 1),
        )
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].home_score, 2)


if __name__ == "__main__":
    unittest.main()
