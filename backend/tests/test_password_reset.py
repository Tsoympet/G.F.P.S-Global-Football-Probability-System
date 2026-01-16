import asyncio
import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.auth_utils import hash_password, verify_password
from backend import google_auth


class PasswordResetSecurityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        models.Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        self.session = SessionLocal()

        user = models.User(
            email="secure@gfps.app",
            password_hash=hash_password("initial-pass123"),
            display_name="User",
            is_active=True,
        )
        self.session.add(user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_reset_token_hashed_and_validates(self):
        captured = {}

        async def fake_send_email(to_email: str, subject: str, body: str):
            captured["body"] = body

        original_send = google_auth.send_email
        google_auth.send_email = fake_send_email
        try:
            asyncio.run(google_auth.request_reset(google_auth.ResetRequest(email="secure@gfps.app"), db=self.session))
        finally:
            google_auth.send_email = original_send

        self.assertIn("reset-password?token=", captured.get("body", ""))
        token_line = [ln for ln in captured["body"].splitlines() if "reset-password?token=" in ln][0]
        token = token_line.split("token=", 1)[1]

        user = self.session.scalar(select(models.User).where(models.User.email == "secure@gfps.app"))
        self.assertIsNotNone(user.reset_token)
        self.assertNotEqual(user.reset_token, token)
        self.assertEqual(len(user.reset_token), 64)  # sha256 hex digest

        result = google_auth.confirm_reset(
            google_auth.ResetConfirm(token=token, new_password="new-secure-pass1"),
            db=self.session,
        )
        self.assertTrue(result["ok"])

        self.session.refresh(user)
        self.assertIsNone(user.reset_token)
        self.assertIsNone(user.reset_token_exp)
        self.assertTrue(verify_password("new-secure-pass1", user.password_hash))
        self.assertEqual(user.token_version, 1)


if __name__ == "__main__":
    unittest.main()
