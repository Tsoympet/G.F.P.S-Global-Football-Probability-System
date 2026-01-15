import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.google_auth import Signup, signup


class SignupIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        models.Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, future=True
        )
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_duplicate_signup_returns_token(self):
        payload = Signup(email="duplicate@gfps.app", password="password123")

        first = signup(payload, db=self.session)
        self.assertTrue(first["token"])

        second = signup(payload, db=self.session)
        self.assertTrue(second["token"])
        self.assertEqual(second["profile"]["email"], payload.email)


if __name__ == "__main__":
    unittest.main()
