import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:////tmp/gfps_test_auth.db"

from backend import db, models
from backend.google_auth import Signup, signup


class SignupIdempotencyTests(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(bind=db.engine)
        models.Base.metadata.create_all(bind=db.engine)
        self.session = db.SessionLocal()

    def tearDown(self):
        self.session.close()
        db.engine.dispose()
        try:
            os.remove("/tmp/gfps_test_auth.db")
        except FileNotFoundError:
            pass

    def test_duplicate_signup_returns_token(self):
        payload = Signup(email="duplicate@gfps.app", password="password123")

        first = signup(payload, db=self.session)
        self.assertTrue(first["token"])

        second = signup(payload, db=self.session)
        self.assertTrue(second["token"])
        self.assertEqual(second["profile"]["email"], payload.email)


if __name__ == "__main__":
    unittest.main()
