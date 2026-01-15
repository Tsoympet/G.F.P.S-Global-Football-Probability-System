import unittest

import numpy as np

from backend.prediction_engine.goals.bivariate_poisson import BivariatePoissonParams, score_probabilities
from backend.prediction_engine.goals.skellam import SkellamParams, skellam_probabilities


class GoalModelTests(unittest.TestCase):
    def test_bivariate_probabilities_sum(self) -> None:
        params = BivariatePoissonParams(lambda_home=1.2, lambda_away=0.9, lambda_shared=0.1)
        prediction = score_probabilities(params, max_goals=6)
        self.assertAlmostEqual(float(prediction.score_matrix.sum()), 1.0, places=6)
        self.assertAlmostEqual(sum(prediction.one_x_two.values()), 1.0, places=6)

    def test_skellam_probabilities_sum(self) -> None:
        params = SkellamParams(lambda_home=1.4, lambda_away=1.1)
        probs = skellam_probabilities(params, max_goals=8)
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
