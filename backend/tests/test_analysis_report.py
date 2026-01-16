"""Tests for analysis report generation."""
import unittest
from datetime import datetime

from backend.analysis.report_engine import (
    generate_professional_report,
    SelectionAnalysis,
)
from backend.correlation.engine import (
    Selection,
    CorrelationResult,
)


class ReportEngineTests(unittest.TestCase):
    """Test professional analysis report generation."""
    
    def test_report_structure(self):
        """Test that report contains all required sections."""
        # Create test data
        selection = Selection(
            client_selection_key="test1",
            fixture_id="123",
            home_team="Team A",
            away_team="Team B",
            league="League 1",
            start_time=datetime.now(),
            market_type="1x2",
            market_name="Match Winner",
            outcome="home",
            odds=2.0,
            prob=0.48
        )
        
        sel_analysis = SelectionAnalysis(
            selection_key="test1",
            match="Team A vs Team B",
            market="Match Winner - home",
            outcome="home",
            odds_bookmaker=2.0,
            odds_fair=2.08,
            probability=0.48,
            ev_roi=0.02,
            data_quality="high",
            confidence="high",
            notes=["Test note"]
        )
        
        correlation = CorrelationResult(
            selection1_key="test1",
            selection2_key="test2",
            coefficient=0.3,
            classification="moderate",
            reason="Test correlation"
        )
        
        # Generate report
        report = generate_professional_report(
            selections=[selection],
            selection_analyses=[sel_analysis],
            correlations=[correlation],
            combined_odds=2.0,
            combined_prob_naive=0.48,
            combined_prob_corr=0.46,
            combined_ev_naive=0.02,
            combined_ev_corr=0.01,
            risk_score=0.3,
            risk_profile="medium"
        )
        
        # Check required sections exist
        self.assertIsNotNone(report.executive_summary)
        self.assertIsNotNone(report.selection_breakdown)
        self.assertIsNotNone(report.correlation_warnings)
        self.assertIsNotNone(report.scenario_analysis)
        self.assertIsNotNone(report.professional_notes)
        self.assertIsNotNone(report.disclaimer)
        
        # Check executive summary keys
        self.assertIn("num_selections", report.executive_summary)
        self.assertIn("combined_odds", report.executive_summary)
        self.assertIn("combined_probability_naive", report.executive_summary)
        self.assertIn("combined_probability_adjusted", report.executive_summary)
        self.assertIn("expected_value_naive", report.executive_summary)
        self.assertIn("expected_value_adjusted", report.executive_summary)
        self.assertIn("risk_score", report.executive_summary)
        self.assertIn("risk_profile", report.executive_summary)
        self.assertIn("key_insight", report.executive_summary)
        
        # Check disclaimer content
        self.assertIn("SIMULATION/ANALYSIS", report.disclaimer)
        self.assertIn("educational and informational purposes", report.disclaimer)
    
    def test_correlation_warning_generation(self):
        """Test correlation warnings are generated correctly."""
        selections = [
            Selection("s1", "100", "A", "B", "L1", None, "1x2", "Winner", "home", 2.0, 0.5),
            Selection("s2", "100", "A", "B", "L1", None, "totals", "O/U", "over", 1.8, 0.55),
        ]
        
        correlations = [
            CorrelationResult("s1", "s2", 0.55, "strong", "BTTS and Over correlation")
        ]
        
        report = generate_professional_report(
            selections=selections,
            selection_analyses=[],
            correlations=correlations,
            combined_odds=3.6,
            combined_prob_naive=0.275,
            combined_prob_corr=0.25,
            combined_ev_naive=0.01,
            combined_ev_corr=-0.01,
            risk_score=0.4,
            risk_profile="medium"
        )
        
        # Should have correlation warnings
        self.assertGreater(len(report.correlation_warnings), 0)
        
        # Check warning structure
        warning = report.correlation_warnings[0]
        self.assertEqual(warning.selection1_key, "s1")
        self.assertEqual(warning.selection2_key, "s2")
        self.assertIn(warning.severity, ["low", "medium", "high", "critical"])
        self.assertIn(warning.correlation_type, ["redundancy", "contradiction"])
    
    def test_scenario_analysis_generation(self):
        """Test scenario analysis is generated."""
        selections = [
            Selection("s1", "100", "A", "B", "L1", None, "1x2", "Winner", "home", 2.0, 0.5),
            Selection("s2", "200", "C", "D", "L1", None, "1x2", "Winner", "away", 2.2, 0.4),
        ]
        
        report = generate_professional_report(
            selections=selections,
            selection_analyses=[],
            correlations=[],
            combined_odds=4.4,
            combined_prob_naive=0.2,
            combined_prob_corr=0.2,
            combined_ev_naive=-0.12,
            combined_ev_corr=-0.12,
            risk_score=0.5,
            risk_profile="medium"
        )
        
        # Should have scenario analysis
        self.assertGreater(len(report.scenario_analysis), 0)
        
        # Check for win requirement scenario
        win_scenarios = [s for s in report.scenario_analysis if s.scenario_type == "win_requirement"]
        self.assertGreater(len(win_scenarios), 0)
        
        # Check for failure point scenarios
        failure_scenarios = [s for s in report.scenario_analysis if s.scenario_type == "failure_point"]
        self.assertGreater(len(failure_scenarios), 0)
    
    def test_professional_notes_generation(self):
        """Test professional notes are generated."""
        selections = [
            Selection("s1", "100", "A", "B", "L1", datetime.now(), "1x2", "Winner", "home", 2.0, 0.5),
        ]
        
        # Use positive EV to trigger opportunity note
        report = generate_professional_report(
            selections=selections,
            selection_analyses=[],
            correlations=[],
            combined_odds=2.0,
            combined_prob_naive=0.5,
            combined_prob_corr=0.5,
            combined_ev_naive=0.08,
            combined_ev_corr=0.08,
            risk_score=0.2,
            risk_profile="low"
        )
        
        # Should have professional notes (opportunity + timing)
        self.assertGreater(len(report.professional_notes), 0)
        
        # Check note categories are valid
        valid_categories = ["market_efficiency", "timing", "trap", "opportunity"]
        for note in report.professional_notes:
            self.assertIn(note.category, valid_categories)


if __name__ == "__main__":
    unittest.main()
