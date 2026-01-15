import unittest

from backend.validation import parse_iso_datetime, parse_market_line, require_decimal_odds


class ValidationTests(unittest.TestCase):
    def test_parse_iso_datetime_normalizes(self):
        self.assertEqual(parse_iso_datetime("2024-01-01T12:00:00Z"), "2024-01-01T12:00:00Z")
        self.assertEqual(parse_iso_datetime("2024-01-01T12:00:00+00:00"), "2024-01-01T12:00:00Z")

    def test_require_decimal_odds(self):
        self.assertEqual(require_decimal_odds(2.1, "odds"), 2.1)
        with self.assertRaises(ValueError):
            require_decimal_odds(1.0, "odds")

    def test_parse_market_line(self):
        self.assertEqual(parse_market_line("2.5"), 2.5)
        with self.assertRaises(ValueError):
            parse_market_line("bad")


if __name__ == "__main__":
    unittest.main()
