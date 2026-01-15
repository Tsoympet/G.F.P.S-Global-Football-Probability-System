import unittest

from backend.db import Base, engine, SessionLocal
from backend.ml_api import _activate_version
from backend.models import ModelActivation, ModelVersion


class ModelActivationTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            db.add(ModelVersion(version="v1", status="ready"))
            db.add(ModelVersion(version="v2", status="ready"))
            db.commit()

    def test_activation_history_and_rollback(self):
        first = _activate_version("v1", activated_by="tester", reason="seed")
        self.assertIsNone(first.previous_version)
        upgrade = _activate_version("v2", activated_by="tester", reason="upgrade")
        self.assertEqual(upgrade.previous_version, "v1")
        rollback = _activate_version("v1", activated_by="tester", reason="rollback", rollback_of="v2")
        self.assertEqual(rollback.rollback_of, "v2")
        with SessionLocal() as db:
            active = (
                db.query(ModelVersion)
                .filter(ModelVersion.status == "active")
                .order_by(ModelVersion.activated_at.desc())
                .first()
            )
            self.assertEqual(active.version, "v1")
            self.assertEqual(db.query(ModelActivation).count(), 3)


if __name__ == "__main__":
    unittest.main()
