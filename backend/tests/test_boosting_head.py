import unittest

from backend.prediction_engine.calibration.boosting_head import BoostingCalibrationHead


class BoostingHeadTests(unittest.TestCase):
    def test_boosting_head_normalizes_and_shifts(self):
        head = BoostingCalibrationHead(learning_rate=0.1, offsets={"home": 0.2, "draw": -0.1, "away": 0.0})
        adjusted = head.adjust({"home": 0.4, "draw": 0.3, "away": 0.3})
        self.assertAlmostEqual(sum(adjusted.values()), 1.0, places=6)
        self.assertGreater(adjusted["home"], 0.4)
        self.assertLess(adjusted["draw"], 0.3)


if __name__ == "__main__":
    unittest.main()
