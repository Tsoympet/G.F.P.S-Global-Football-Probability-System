"""Tests for the WebScraperProvider."""
from pathlib import Path
from datetime import datetime

import pytest

from backend.data_providers import WebScraperProvider, FixtureRecord, ResultRecord


def test_web_scraper_initialization():
    """Test that WebScraperProvider can be initialized."""
    provider = WebScraperProvider(allow_network=False)
    assert provider.meta.name == "web-scraper"
    assert "fixtures" in provider.meta.data_types
    assert "results" in provider.meta.data_types


def test_web_scraper_with_empty_config():
    """Test that scraper returns empty lists when not configured."""
    provider = WebScraperProvider(allow_network=False, config={})
    
    fixtures = list(provider.get_fixtures())
    results = list(provider.get_results())
    
    assert fixtures == []
    assert results == []


def test_web_scraper_parses_fixtures_from_html():
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
    
    assert len(fixtures) == 2
    assert fixtures[0].fixture_id == "12345"
    assert fixtures[0].home_team == "Team A"
    assert fixtures[0].away_team == "Team B"
    assert fixtures[0].league == "Premier League"
    assert fixtures[1].fixture_id == "12346"
    assert fixtures[1].home_team == "Team C"


def test_web_scraper_parses_results_from_html():
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
    
    assert len(results) == 1
    assert results[0].fixture_id == "12345"
    assert results[0].home_team == "Team A"
    assert results[0].away_team == "Team B"
    assert results[0].home_score == 2
    assert results[0].away_score == 1
    assert results[0].status == "FT"


def test_web_scraper_handles_malformed_html():
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
    assert len(fixtures) == 1
    assert fixtures[0].home_team == "Team A"
    assert fixtures[0].away_team == "TBD"


def test_web_scraper_rate_limiting():
    """Test that rate limiting delays requests appropriately."""
    import time
    
    provider = WebScraperProvider(allow_network=False)
    provider._min_request_interval = 0.1  # 100ms for testing
    
    start = time.time()
    provider._rate_limit()
    provider._rate_limit()
    elapsed = time.time() - start
    
    # Should have waited at least the minimum interval
    assert elapsed >= 0.1


def test_web_scraper_cache_path_generation():
    """Test that cache paths are generated correctly."""
    provider = WebScraperProvider(allow_network=False)
    
    url1 = "http://example.com/fixtures"
    url2 = "http://example.com/results"
    
    path1 = provider._get_cache_path(url1)
    path2 = provider._get_cache_path(url2)
    
    # Different URLs should generate different cache paths
    assert path1 != path2
    assert path1.suffix == ".html"
    assert path2.suffix == ".html"


def test_web_scraper_disabled_when_network_off():
    """Test that scraper doesn't make requests when network is disabled."""
    config = {
        "fixtures_url": "http://example.com/fixtures",
        "selectors": {"fixture_container": ".match"}
    }
    
    provider = WebScraperProvider(allow_network=False, config=config)
    
    # Should return empty list without attempting network request
    html = provider._fetch_html("http://example.com/fixtures", use_cache=False)
    assert html is None
