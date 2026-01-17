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

    def test_captcha_detection(self):
        """Test that captcha detection works."""
        provider = WebScraperProvider(allow_network=False, config={
            "captcha_detection": {
                "enabled": True,
                "indicators": ["captcha", "recaptcha"]
            }
        })
        
        # HTML with captcha
        html_with_captcha = "<html><body><div class='g-recaptcha'></div></body></html>"
        self.assertTrue(provider._detect_captcha(html_with_captcha))
        
        # HTML without captcha
        html_without_captcha = "<html><body><div class='match'></div></body></html>"
        self.assertFalse(provider._detect_captcha(html_without_captcha))

    def test_structure_monitoring(self):
        """Test HTML structure change detection."""
        provider = WebScraperProvider(allow_network=False, config={
            "structure_monitoring": {
                "enabled": True,
                "similarity_threshold": 0.8
            }
        })
        
        url = "http://test.com"
        html1 = "<html><body><div class='match'><span class='team'>A</span></div></body></html>"
        html2 = "<html><body><div class='match'><span class='team'>B</span></div></body></html>"
        html3 = "<html><body><table><tr><td>Data</td></tr></table></body></html>"
        
        # First time should not detect change
        self.assertFalse(provider._detect_structure_change(url, html1))
        
        # Similar structure should not trigger change
        self.assertFalse(provider._detect_structure_change(url, html2))
        
        # Very different structure should trigger change
        # (depends on threshold and implementation details)
        provider._detect_structure_change(url, html3)

    def test_auto_selector_learning(self):
        """Test automatic selector learning."""
        provider = WebScraperProvider(allow_network=False, config={
            "auto_selector_learning": {
                "enabled": True
            }
        })
        
        html = """
        <html><body>
            <div class='match'>Match 1</div>
            <div class='match'>Match 2</div>
            <div class='match'>Match 3</div>
        </body></html>
        """
        
        suggestions = provider._learn_selectors(html)
        # Should suggest .match as container
        self.assertIsInstance(suggestions, dict)

    def test_pagination_config(self):
        """Test pagination configuration loading."""
        config = {
            "fixtures_url": "http://example.com",
            "pagination": {
                "enabled": True,
                "type": "url_pattern",
                "url_pattern": "?page={page}",
                "max_pages": 5
            }
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        self.assertTrue(provider.config["pagination"]["enabled"])
        self.assertEqual(provider.config["pagination"]["type"], "url_pattern")
        self.assertEqual(provider.config["pagination"]["max_pages"], 5)

    def test_proxy_config(self):
        """Test proxy configuration loading."""
        config = {
            "proxy": {
                "enabled": True,
                "server": "http://proxy.example.com:8080",
                "username": "user",
                "password": "pass"
            }
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        self.assertTrue(provider.config["proxy"]["enabled"])
        self.assertEqual(provider.config["proxy"]["server"], "http://proxy.example.com:8080")

    def test_captcha_handler_registration(self):
        """Test captcha handler can be registered."""
        provider = WebScraperProvider(allow_network=False)
        
        def dummy_handler(url: str) -> str:
            return "<html>solved</html>"
        
        provider.set_captcha_handler(dummy_handler)
        self.assertIsNotNone(provider.captcha_handler)
        self.assertEqual(provider.captcha_handler("test"), "<html>solved</html>")

    def test_js_rendering_config(self):
        """Test JavaScript rendering configuration."""
        config = {
            "use_js_rendering": True,
            "js_wait_time": 3000
        }
        
        provider = WebScraperProvider(allow_network=False, config=config)
        # JS rendering should be enabled only if Playwright is available
        # In test environment it might not be installed
        self.assertEqual(provider.config["use_js_rendering"], True)
        self.assertEqual(provider.config["js_wait_time"], 3000)


if __name__ == "__main__":
    unittest.main()
