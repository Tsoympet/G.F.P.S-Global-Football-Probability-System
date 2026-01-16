import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import ingestion_pipeline
from backend.data_providers import OpenFootballCSVProvider
from backend.models import Base, FixtureEntity, ResultEntity


class IngestionFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine, future=True)
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_ingest_and_feature_build(self):
        provider = OpenFootballCSVProvider(base_path=Path("backend/sample_data"))
        stats = ingestion_pipeline.ingest_fixtures(
            session=self.session, providers=[provider], db_engine=self.engine
        )
        self.assertGreater(stats["fixtures"], 0)
        self.assertGreater(stats["results"], 0)

        features = ingestion_pipeline.build_features(
            session=self.session, db_engine=self.engine
        )
        self.assertTrue(features)
        # ensure persistence
        self.assertGreater(self.session.query(FixtureEntity).count(), 0)
        self.assertGreater(self.session.query(ResultEntity).count(), 0)


if __name__ == "__main__":
    unittest.main()
