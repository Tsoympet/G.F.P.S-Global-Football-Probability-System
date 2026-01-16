import asyncio
import re
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse

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

        with mock.patch("backend.google_auth.send_email", fake_send_email):
            asyncio.run(google_auth.request_reset(google_auth.ResetRequest(email="secure@gfps.app"), db=self.session))

        body = captured.get("body", "")
        url_match = re.search(r"https?://\S+", body)
        self.assertIsNotNone(url_match)
        parsed = urlparse(url_match.group(0).strip())
        token_values = parse_qs(parsed.query).get("token", [])
        self.assertTrue(token_values)
        token = token_values[0]

        user = self.session.scalar(select(models.User).where(models.User.email == "secure@gfps.app"))
        self.assertIsNotNone(user.reset_token)
        self.assertNotEqual(user.reset_token, token)
        self.assertEqual(len(user.reset_token), google_auth.RESET_TOKEN_HASH_LEN)

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
