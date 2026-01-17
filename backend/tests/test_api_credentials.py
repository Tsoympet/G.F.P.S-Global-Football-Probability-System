import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.google_auth import (
    Signup,
    signup,
    ApiProviderCredentials,
    save_api_credentials,
    get_api_credentials,
)


class ApiCredentialsTests(unittest.TestCase):
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

    def test_save_and_retrieve_api_credentials(self):
        # Create a user first
        signup_data = Signup(email="test@example.com", password="password123")
        signup_result = signup(signup_data, db=self.session)
        
        # Get the user from DB
        user = (
            self.session.query(models.User)
            .filter(models.User.email == "test@example.com")
            .first()
        )
        self.assertIsNotNone(user)
        
        # Save API credentials
        credentials_data = ApiProviderCredentials(
            credentials={
                "api-football": "test-key-123",
                "football-data": "test-key-456",
            }
        )
        save_result = save_api_credentials(credentials_data, user=user, db=self.session)
        self.assertEqual(save_result["provider_count"], 2)
        
        # Retrieve API credentials
        get_result = get_api_credentials(user=user, db=self.session)
        self.assertEqual(get_result["provider_count"], 2)
        self.assertEqual(get_result["credentials"]["api-football"], "test-key-123")
        self.assertEqual(get_result["credentials"]["football-data"], "test-key-456")

    def test_empty_credentials_on_new_user(self):
        # Create a user
        signup_data = Signup(email="newuser@example.com", password="password123")
        signup(signup_data, db=self.session)
        
        # Get the user
        user = (
            self.session.query(models.User)
            .filter(models.User.email == "newuser@example.com")
            .first()
        )
        
        # Get credentials (should be empty)
        get_result = get_api_credentials(user=user, db=self.session)
        self.assertEqual(get_result["provider_count"], 0)
        self.assertEqual(get_result["credentials"], {})


if __name__ == "__main__":
    unittest.main()
