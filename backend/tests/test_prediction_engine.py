import unittest
from dataclasses import replace

from backend.prediction_engine.engine import PredictionEngine, PredictionInput
from backend.prediction_engine.strength.team_strength import MatchResult
from backend.prediction_engine import predict_market


class PredictionEngineTests(unittest.TestCase):
    def setUp(self):
        self.results = [
            MatchResult(home_team="Alpha FC", away_team="Beta FC", home_goals=2, away_goals=1, league="Test"),
            MatchResult(home_team="Beta FC", away_team="Alpha FC", home_goals=0, away_goals=0, league="Test"),
            MatchResult(home_team="Alpha FC", away_team="Gamma FC", home_goals=3, away_goals=1, league="Test"),
        ]
        self.base_input = PredictionInput(
            fixture_id="fx-1",
            league="Test",
            home_team="Alpha FC",
            away_team="Beta FC",
            odds={"home": 2.1, "draw": 3.3, "away": 3.4},
            recent_results=self.results,
            base_home_goals=1.5,
            base_away_goals=1.1,
            home_attack=1.1,
            away_attack=0.9,
            home_defence=0.95,
            away_defence=1.05,
            form_home=0.7,
            form_away=0.4,
            dixon_coles_rho=-0.08,
        )

    def test_probabilities_sum_to_one(self):
        engine = PredictionEngine()
        output = engine.predict(self.base_input)
        probs = output["probabilities"]
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=6)
        for value in probs.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_form_shift_boosts_home(self):
        engine = PredictionEngine()
        neutral = replace(self.base_input, form_home=0.5, form_away=0.5)
        boosted = replace(self.base_input, form_home=0.8, form_away=0.3)
        neutral_matrix = engine.poisson_prediction(neutral).score_matrix
        boosted_matrix = engine.poisson_prediction(boosted).score_matrix
        home_goals = list(range(neutral_matrix.shape[0]))
        neutral_xg = float((neutral_matrix.sum(axis=1) * home_goals).sum())
        boosted_xg = float((boosted_matrix.sum(axis=1) * home_goals).sum())
        self.assertGreater(boosted_xg, neutral_xg)

    def test_predict_market_over_under(self):
        ctx = {
            "league_id": "test",
            "home_team": "Alpha FC",
            "away_team": "Beta FC",
            "home_attack": 1.05,
            "away_attack": 0.95,
            "home_defense": 0.98,
            "away_defense": 1.02,
        }
        odds = {"Over 2.5": 1.9, "Under 2.5": 2.0}
        response = predict_market("Over/Under 2.5", odds, ctx)
        self.assertEqual(set(response.keys()), set(odds.keys()))
        total_prob = sum(item["prob"] for item in response.values())
        self.assertAlmostEqual(total_prob, 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
