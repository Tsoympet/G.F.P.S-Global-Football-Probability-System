"""Tests for correlation detection engine."""
import unittest
from datetime import datetime, timedelta

from backend.correlation.engine import (
    Selection,
    detect_correlations,
    compute_effective_legs,
    _same_match_correlation,
    _same_team_correlation,
)


class CorrelationEngineTests(unittest.TestCase):
    """Test correlation detection and classification."""
    
    def test_same_match_1x2_totals_correlation(self):
        """Test 1X2 and Over/Under correlation on same match."""
        s1 = Selection(
            client_selection_key="sel1",
            fixture_id="123",
            home_team="Team A",
            away_team="Team B",
            league="League 1",
            start_time=None,
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.0,
            prob=0.45
        )
        s2 = Selection(
            client_selection_key="sel2",
            fixture_id="123",
            home_team="Team A",
            away_team="Team B",
            league="League 1",
            start_time=None,
            market_type="totals",
            market_name="Over/Under 2.5",
            outcome="over",
            odds=1.8,
            prob=0.55
        )
        
        corr = _same_match_correlation(s1, s2)
        self.assertIsNotNone(corr)
        self.assertEqual(corr.classification, "moderate")
        self.assertAlmostEqual(corr.coefficient, 0.30, places=2)
    
    def test_same_match_btts_totals_correlation(self):
        """Test BTTS and Over/Under correlation on same match."""
        s1 = Selection(
            client_selection_key="sel1",
            fixture_id="456",
            home_team="Team C",
            away_team="Team D",
            league="League 1",
            start_time=None,
            market_type="btts",
            market_name="Both Teams To Score",
            outcome="yes",
            odds=1.9,
            prob=0.52
        )
        s2 = Selection(
            client_selection_key="sel2",
            fixture_id="456",
            home_team="Team C",
            away_team="Team D",
            league="League 1",
            start_time=None,
            market_type="totals",
            market_name="Over/Under 2.5",
            outcome="over",
            odds=1.75,
            prob=0.57
        )
        
        corr = _same_match_correlation(s1, s2)
        self.assertIsNotNone(corr)
        self.assertEqual(corr.classification, "strong")
        self.assertAlmostEqual(corr.coefficient, 0.55, places=2)
    
    def test_same_match_handicap_1x2_correlation(self):
        """Test Handicap and Match Result correlation on same match."""
        s1 = Selection(
            client_selection_key="sel1",
            fixture_id="789",
            home_team="Team E",
            away_team="Team F",
            league="League 1",
            start_time=None,
            market_type="handicap",
            market_name="Asian Handicap -0.5",
            outcome="home",
            odds=1.95,
            prob=0.50
        )
        s2 = Selection(
            client_selection_key="sel2",
            fixture_id="789",
            home_team="Team E",
            away_team="Team F",
            league="League 1",
            start_time=None,
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.1,
            prob=0.47
        )
        
        corr = _same_match_correlation(s1, s2)
        self.assertIsNotNone(corr)
        self.assertEqual(corr.classification, "strong")
        self.assertAlmostEqual(corr.coefficient, 0.60, places=2)
    
    def test_same_team_correlation(self):
        """Test same team across different matches."""
        now = datetime.now()
        s1 = Selection(
            client_selection_key="sel1",
            fixture_id="111",
            home_team="Team X",
            away_team="Team Y",
            league="League 1",
            start_time=now,
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.0,
            prob=0.48
        )
        s2 = Selection(
            client_selection_key="sel2",
            fixture_id="222",
            home_team="Team X",
            away_team="Team Z",
            league="League 1",
            start_time=now + timedelta(days=2),
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=1.9,
            prob=0.51
        )
        
        corr = _same_team_correlation(s1, s2)
        self.assertIsNotNone(corr)
        self.assertEqual(corr.classification, "weak")
        self.assertAlmostEqual(corr.coefficient, 0.20, places=2)
    
    def test_redundant_selection(self):
        """Test duplicate selection detection."""
        s1 = Selection(
            client_selection_key="sel1",
            fixture_id="999",
            home_team="Team A",
            away_team="Team B",
            league="League 1",
            start_time=None,
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.0,
            prob=0.5
        )
        s2 = Selection(
            client_selection_key="sel2",
            fixture_id="999",
            home_team="Team A",
            away_team="Team B",
            league="League 1",
            start_time=None,
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.0,
            prob=0.5
        )
        
        corr = _same_match_correlation(s1, s2)
        self.assertIsNotNone(corr)
        self.assertEqual(corr.classification, "redundant")
        self.assertGreaterEqual(corr.coefficient, 0.9)
    
    def test_effective_legs_calculation(self):
        """Test effective legs calculation with correlations."""
        from backend.correlation.engine import CorrelationResult
        
        # 3 selections with moderate correlation
        correlations = [
            CorrelationResult("s1", "s2", 0.3, "moderate", "test"),
            CorrelationResult("s2", "s3", 0.3, "moderate", "test"),
        ]
        
        n_eff, rho_mean = compute_effective_legs(3, correlations, alpha=1.0)
        
        # With positive correlations, effective legs should be less than actual
        self.assertLess(n_eff, 3.0)
        self.assertGreater(n_eff, 1.0)
        self.assertAlmostEqual(rho_mean, 0.3, places=2)
    
    def test_effective_legs_no_correlation(self):
        """Test effective legs with no correlations (independent)."""
        n_eff, rho_mean = compute_effective_legs(5, [], alpha=1.0)
        
        # No correlations = independent = n_eff = n
        self.assertAlmostEqual(n_eff, 5.0, places=1)
        self.assertAlmostEqual(rho_mean, 0.0, places=2)
    
    def test_detect_correlations_integration(self):
        """Test full correlation detection pipeline."""
        now = datetime.now()
        selections = [
            Selection("s1", "100", "A", "B", "L1", now, "1x2", "Winner", "home", 2.0, 0.5),
            Selection("s2", "100", "A", "B", "L1", now, "totals", "O/U 2.5", "over", 1.8, 0.55),
            Selection("s3", "200", "C", "D", "L1", now + timedelta(days=1), "1x2", "Winner", "away", 2.2, 0.45),
        ]
        
        correlations = detect_correlations(selections)
        
        # Should detect s1-s2 same match correlation
        self.assertGreater(len(correlations), 0)
        
        # Check that same match correlation exists
        same_match_corr = [c for c in correlations if c.selection1_key == "s1" and c.selection2_key == "s2"]
        self.assertEqual(len(same_match_corr), 1)
        self.assertEqual(same_match_corr[0].classification, "moderate")


class AccumulatorMathTests(unittest.TestCase):
    """Test accumulator probability and EV calculations."""
    
    def test_naive_probability_calculation(self):
        """Test naive independence probability calculation."""
        probs = [0.5, 0.6, 0.7]
        naive_prob = 1.0
        for p in probs:
            naive_prob *= p
        
        expected = 0.5 * 0.6 * 0.7
        self.assertAlmostEqual(naive_prob, expected, places=6)
        self.assertAlmostEqual(naive_prob, 0.21, places=2)
    
    def test_correlation_adjusted_probability(self):
        """Test correlation-adjusted probability calculation."""
        # P_corr = P_naive^(N/N_eff)
        p_naive = 0.21
        n = 3
        n_eff = 2.5
        
        exponent = n / n_eff
        p_corr = p_naive ** exponent
        
        # With n_eff < n, exponent > 1, so p_corr < p_naive
        self.assertLess(p_corr, p_naive)
    
    def test_combined_odds_calculation(self):
        """Test combined odds calculation (product)."""
        odds_list = [2.0, 1.8, 2.2]
        combined = 1.0
        for odds in odds_list:
            combined *= odds
        
        expected = 2.0 * 1.8 * 2.2
        self.assertAlmostEqual(combined, expected, places=6)
        self.assertAlmostEqual(combined, 7.92, places=2)


if __name__ == "__main__":
    unittest.main()
