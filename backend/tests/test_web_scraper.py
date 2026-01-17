"""Tests for the WebScraperProvider."""
import json
import unittest
from pathlib import Path
from datetime import datetime

from backend.data_providers import WebScraperProvider, FixtureRecord, ResultRecord


class WebScraperTests(unittest.TestCase):
    def test_web_scraper_initialization(self):
        """Test that WebScraperProvider can be initialized."""
        provider = WebScraperProvider(allow_network=False)
        self.assertEqual(provider.meta.name, "web-scraper")
        self.assertIn("fixtures", provider.meta.data_types)
        self.assertIn("results", provider.meta.data_types)


    def test_web_scraper_with_empty_config(self):
        """Test that scraper returns empty lists when not configured."""
        provider = WebScraperProvider(allow_network=False, config={})
        
        fixtures = list(provider.get_fixtures())
        results = list(provider.get_results())
        
        self.assertEqual(fixtures, [])
        self.assertEqual(results, [])


    def test_web_scraper_parses_fixtures_from_html(self):
        """Test parsing fixtures from sample HTML."""
        html = """
        <html>
            <body>
                <div class="match">
                    <span class="id">12345</span>
                    <span class="home">Team A</span>
                    <span class="away">Team B</span>
                    <span class="league">Premier League</span>
                    <span class="season">2024</span>
                    <time class="kickoff">2024-12-25T15:00:00Z</time>
                    <span class="venue">Stadium A</span>
                </div>
                <div class="match">
                    <span class="id">12346</span>
                    <span class="home">Team C</span>
                    <span class="away">Team D</span>
                    <span class="league">La Liga</span>
                    <span class="season">2024</span>
                    <time class="kickoff">2024-12-26T18:00:00Z</time>
                    <span class="venue">Stadium B</span>
                </div>
            </body>
        </html>
        """
        
        config = {
            "fixtures_url": "http://example.com/fixtures",
            "selectors": {
                "fixture_container": ".match",
                "fixture_id": ".id",
                "home_team": ".home",
                "away_team": ".away",
                "league": ".league",
                "season": ".season",
                "kickoff": ".kickoff",
                "venue": ".venue",
            }
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        fixtures = provider._extract_fixtures_from_html(html)
        
        self.assertEqual(len(fixtures), 2)
        self.assertEqual(fixtures[0].fixture_id, "12345")
        self.assertEqual(fixtures[0].home_team, "Team A")
        self.assertEqual(fixtures[0].away_team, "Team B")
        self.assertEqual(fixtures[0].league, "Premier League")
        self.assertEqual(fixtures[1].fixture_id, "12346")
        self.assertEqual(fixtures[1].home_team, "Team C")


    def test_web_scraper_parses_results_from_html(self):
        """Test parsing results from sample HTML."""
        html = """
        <html>
            <body>
                <div class="match">
                    <span class="id">12345</span>
                    <span class="home">Team A</span>
                    <span class="away">Team B</span>
                    <span class="league">Premier League</span>
                    <span class="season">2024</span>
                    <time class="kickoff">2024-12-20T15:00:00Z</time>
                    <span class="home-score">2</span>
                    <span class="away-score">1</span>
                    <span class="status">FT</span>
                </div>
            </body>
        </html>
        """
        
        config = {
            "results_url": "http://example.com/results",
            "selectors": {
                "fixture_container": ".match",
                "fixture_id": ".id",
                "home_team": ".home",
                "away_team": ".away",
                "league": ".league",
                "season": ".season",
                "kickoff": ".kickoff",
            },
            "result_selectors": {
                "home_score": ".home-score",
                "away_score": ".away-score",
                "status": ".status",
            }
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        results = provider._extract_results_from_html(html)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].fixture_id, "12345")
        self.assertEqual(results[0].home_team, "Team A")
        self.assertEqual(results[0].away_team, "Team B")
        self.assertEqual(results[0].home_score, 2)
        self.assertEqual(results[0].away_score, 1)
        self.assertEqual(results[0].status, "FT")


    def test_web_scraper_handles_malformed_html(self):
        """Test that scraper handles malformed HTML gracefully."""
        html = """
        <html>
            <body>
                <div class="match">
                    <span class="home">Team A</span>
                    <!-- Missing away team -->
                </div>
            </body>
        </html>
        """
        
        config = {
            "fixtures_url": "http://example.com/fixtures",
            "selectors": {
                "fixture_container": ".match",
                "fixture_id": ".id",
                "home_team": ".home",
                "away_team": ".away",
                "league": ".league",
                "season": ".season",
                "kickoff": ".kickoff",
            }
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        fixtures = provider._extract_fixtures_from_html(html)
        
        # Should still create a fixture with default values for missing fields
        self.assertEqual(len(fixtures), 1)
        self.assertEqual(fixtures[0].home_team, "Team A")
        self.assertEqual(fixtures[0].away_team, "TBD")


    def test_web_scraper_rate_limiting(self):
        """Test that rate limiting delays requests appropriately."""
        import time
        
        provider = WebScraperProvider(allow_network=False)
        provider._min_request_interval = 0.1  # 100ms for testing
        
        start = time.time()
        provider._rate_limit()
        provider._rate_limit()
        elapsed = time.time() - start
        
        # Should have waited at least the minimum interval
        self.assertGreaterEqual(elapsed, 0.1)


    def test_web_scraper_cache_path_generation(self):
        """Test that cache paths are generated correctly."""
        provider = WebScraperProvider(allow_network=False)
        
        url1 = "http://example.com/fixtures"
        url2 = "http://example.com/results"
        
        path1 = provider._get_cache_path(url1)
        path2 = provider._get_cache_path(url2)
        
        # Different URLs should generate different cache paths
        self.assertNotEqual(path1, path2)
        self.assertEqual(path1.suffix, ".html")
        self.assertEqual(path2.suffix, ".html")


    def test_web_scraper_disabled_when_network_off(self):
        """Test that scraper doesn't make requests when network is disabled."""
        config = {
            "fixtures_url": "http://example.com/fixtures",
            "selectors": {"fixture_container": ".match"}
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        
        # Should return empty list without attempting network request
        html = provider._fetch_html("http://example.com/fixtures", use_cache=False)
        self.assertIsNone(html)


    def test_web_scraper_loads_config_from_env(self):
        """Test that scraper loads config from SCRAPER_CONFIG_PATH env variable."""
        import tempfile
        import os
        
        # Create a temporary config file
        config_data = {
            "fixtures_url": "http://env-test.com/fixtures",
            "selectors": {"fixture_container": ".env-match"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            # Set environment variable
            os.environ["SCRAPER_CONFIG_PATH"] = temp_path
            
            # Create provider without explicit config
            provider = WebScraperProvider(allow_network=False)
            
            # Should load from env variable
            self.assertEqual(provider.config["fixtures_url"], "http://env-test.com/fixtures")
            self.assertEqual(provider.config["selectors"]["fixture_container"], ".env-match")
        finally:
            # Clean up
            if "SCRAPER_CONFIG_PATH" in os.environ:
                del os.environ["SCRAPER_CONFIG_PATH"]
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
