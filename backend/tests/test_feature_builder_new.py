import unittest
from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.feature_builder import build_match_features
from backend.models import Base, FixtureEntity, ResultEntity


class FeatureBuilderTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine, future=True)
        self.session = Session()

        # historical results for both teams
        fixtures = [
            FixtureEntity(
                fixture_id="HIST-1",
                provider="test",
                league="Premier League",
                season="2024",
                home_team="Arsenal",
                away_team="Chelsea",
                kickoff_utc=datetime.now(timezone.utc) - timedelta(days=10),
            ),
            FixtureEntity(
                fixture_id="HIST-2",
                provider="test",
                league="Premier League",
                season="2024",
                home_team="Chelsea",
                away_team="Arsenal",
                kickoff_utc=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            FixtureEntity(
                fixture_id="TARGET",
                provider="test",
                league="Premier League",
                season="2024",
                home_team="Arsenal",
                away_team="Chelsea",
                kickoff_utc=datetime.now(timezone.utc) + timedelta(days=1),
            ),
        ]
        for f in fixtures:
            self.session.add(f)

        self.session.add(ResultEntity(fixture_id="HIST-1", provider="test", home_score=2, away_score=1))
        self.session.add(ResultEntity(fixture_id="HIST-2", provider="test", home_score=0, away_score=3))
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_build_features(self):
        features = build_match_features(self.session, "TARGET")
        self.assertIn("lambda_home", features)
        self.assertGreater(features["home_xg_proxy"]["for"], 0)
        self.assertGreaterEqual(features["home_form"], 0)


if __name__ == "__main__":
    unittest.main()
