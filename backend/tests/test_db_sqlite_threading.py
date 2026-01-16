import unittest

from backend.db import engine, CONNECT_ARGS


class SQLiteThreadingConfigTests(unittest.TestCase):
    def test_sqlite_allows_cross_thread(self):
        # Only run when using SQLite (default for CI smoke tests)
        if not engine.url.drivername.startswith("sqlite"):
            self.skipTest("Non-sqlite backend configured")

        self.assertIn("check_same_thread", CONNECT_ARGS)
        self.assertFalse(CONNECT_ARGS["check_same_thread"])


if __name__ == "__main__":
    unittest.main()
