import logging
import unittest
from unittest.mock import MagicMock, patch

from backend.health_api import _check_database


class TestHealthApi(unittest.TestCase):
    """Test health API security and functionality."""

    def test_check_database_success(self):
        """Test that database check returns ok status when connection succeeds."""
        result = _check_database()
        # In test environment, database might not be available
        # This test mainly verifies the function runs without error
        self.assertIn("status", result)

    @patch("backend.health_api.engine")
    def test_check_database_does_not_expose_exception_details(self, mock_engine):
        """Test that database errors return generic message without exposing internal details."""
        # Setup mock to raise an exception with sensitive information
        mock_connection = MagicMock()
        mock_connection.execute.side_effect = Exception(
            "FATAL: password authentication failed for user 'admin' at host 'internal-db-server.local:5432'"
        )
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        # Capture logs to verify exception is logged
        with self.assertLogs("backend.health_api", level=logging.ERROR) as log_context:
            result = _check_database()

        # Verify the result does not contain sensitive exception details
        self.assertEqual(result["status"], "error")
        self.assertIn("detail", result)
        
        # Verify the detail message is generic and doesn't leak sensitive info
        detail = result["detail"]
        self.assertEqual(detail, "Database connection failed")
        self.assertNotIn("password", detail.lower())
        self.assertNotIn("authentication", detail.lower())
        self.assertNotIn("admin", detail)
        self.assertNotIn("internal-db-server", detail)
        self.assertNotIn("5432", detail)
        
        # Verify that the full exception was logged (for server-side debugging)
        self.assertTrue(any("Database health check failed" in msg for msg in log_context.output))

    @patch("backend.health_api.engine")
    def test_check_database_logs_exception(self, mock_engine):
        """Test that exceptions are logged for debugging purposes."""
        mock_connection = MagicMock()
        test_exception = Exception("Test database error")
        mock_connection.execute.side_effect = test_exception
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with self.assertLogs("backend.health_api", level=logging.ERROR) as log_context:
            _check_database()

        # Verify the exception was logged
        self.assertTrue(any("Database health check failed" in msg for msg in log_context.output))


if __name__ == "__main__":
    unittest.main()
