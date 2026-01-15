import unittest

from backend.value.ev import expected_value


class ValueEngineTests(unittest.TestCase):
    def test_expected_value_formula(self):
        self.assertAlmostEqual(expected_value(0.5, 2.0), 0.0, places=6)
        self.assertAlmostEqual(expected_value(0.6, 1.8), 0.08, places=6)


if __name__ == "__main__":
    unittest.main()
