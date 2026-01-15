import unittest

import numpy as np

from backend.prediction_engine.calibration.conformal import ConformalPredictor


class CalibrationTests(unittest.TestCase):
    def test_conformal_predictor_sets(self) -> None:
        probs = np.array(
            [
                [0.6, 0.2, 0.2],
                [0.3, 0.4, 0.3],
                [0.2, 0.2, 0.6],
                [0.5, 0.25, 0.25],
            ]
        )
        labels = np.array([0, 1, 2, 0])
        predictor = ConformalPredictor.fit(probs, labels, alpha=0.1)
        sets = predictor.predict_set(probs)
        self.assertEqual(sets.shape, probs.shape)
        self.assertTrue(np.all(sets.sum(axis=1) >= 1))


if __name__ == "__main__":
    unittest.main()
