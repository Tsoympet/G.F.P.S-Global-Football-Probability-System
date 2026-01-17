#!/usr/bin/env python3
"""
Demo script showing how to use the WebScraperProvider.

This script demonstrates:
1. Creating a web scraper provider with custom configuration
2. Scraping fixtures from HTML
3. Scraping results from HTML
4. Integration with the data ingestion pipeline
"""

from backend.data_providers import WebScraperProvider


def demo_basic_usage():
    """Demonstrate basic web scraper usage."""
    print("=" * 60)
    print("Demo 1: Basic Web Scraper Usage")
    print("=" * 60)
    
    # Configure the scraper
    config = {
        "fixtures_url": "http://example.com/fixtures",
        "results_url": "http://example.com/results",
        "selectors": {
            "fixture_container": ".match",
            "fixture_id": "[data-match-id]",
            "home_team": ".team.home",
            "away_team": ".team.away",
            "kickoff": "time[datetime]",
            "league": ".league-name",
            "season": ".season",
            "venue": ".venue"
        },
        "result_selectors": {
            "home_score": ".score.home",
            "away_score": ".score.away",
            "status": ".match-status"
        }
    }
    
    # Create the provider (network disabled for demo)
    provider = WebScraperProvider(config=config, allow_network=False)
    
    print(f"\n✓ Created provider: {provider.meta.name}")
    print(f"  Priority: {provider.meta.priority}")
    print(f"  Reliability: {provider.meta.reliability}")
    print(f"  Rate limit: {provider.meta.rate_limit_per_minute} requests/min")
    print(f"  Cache refresh: {provider.meta.refresh_seconds} seconds")


def demo_parsing_fixtures():
    """Demonstrate parsing fixtures from HTML."""
    print("\n" + "=" * 60)
    print("Demo 2: Parsing Fixtures from HTML")
    print("=" * 60)
    
    config = {
        "selectors": {
            "fixture_container": "div.match",
            "fixture_id": "span.id",
            "home_team": "span.home",
            "away_team": "span.away",
            "league": "span.league",
            "season": "span.season",
            "kickoff": "time.datetime",
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    # Sample HTML
    sample_html = """
    <html>
        <body>
            <div class="match">
                <span class="id">12345</span>
                <span class="home">Manchester United</span>
                <span class="away">Liverpool</span>
                <span class="league">Premier League</span>
                <span class="season">2024/25</span>
                <time class="datetime">2024-12-26T15:00:00Z</time>
            </div>
            <div class="match">
                <span class="id">12346</span>
                <span class="home">Chelsea</span>
                <span class="away">Arsenal</span>
                <span class="league">Premier League</span>
                <span class="season">2024/25</span>
                <time class="datetime">2024-12-26T17:30:00Z</time>
            </div>
        </body>
    </html>
    """
    
    # Parse fixtures
    fixtures = provider._extract_fixtures_from_html(sample_html)
    
    print(f"\n✓ Parsed {len(fixtures)} fixtures:")
    for fixture in fixtures:
        print(f"  [{fixture.fixture_id}] {fixture.home_team} vs {fixture.away_team}")
        print(f"    League: {fixture.league}, Season: {fixture.season}")
        print(f"    Kickoff: {fixture.kickoff}")


def demo_parsing_results():
    """Demonstrate parsing results from HTML."""
    print("\n" + "=" * 60)
    print("Demo 3: Parsing Results from HTML")
    print("=" * 60)
    
    config = {
        "selectors": {
            "fixture_container": "tr.result-row",
            "fixture_id": "td.match-id",
            "home_team": "td.home-team",
            "away_team": "td.away-team",
            "league": "td.league",
            "season": "td.season",
            "kickoff": "td.date",
        },
        "result_selectors": {
            "home_score": "td.home-score",
            "away_score": "td.away-score",
            "status": "td.status"
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    # Sample HTML (table format)
    sample_html = """
    <html>
        <table class="results">
            <tbody>
                <tr class="result-row">
                    <td class="match-id">98765</td>
                    <td class="home-team">Real Madrid</td>
                    <td class="away-team">Barcelona</td>
                    <td class="league">La Liga</td>
                    <td class="season">2024/25</td>
                    <td class="date">2024-12-20T20:00:00Z</td>
                    <td class="home-score">2</td>
                    <td class="away-score">1</td>
                    <td class="status">FT</td>
                </tr>
                <tr class="result-row">
                    <td class="match-id">98766</td>
                    <td class="home-team">Bayern Munich</td>
                    <td class="away-team">Borussia Dortmund</td>
                    <td class="league">Bundesliga</td>
                    <td class="season">2024/25</td>
                    <td class="date">2024-12-21T17:30:00Z</td>
                    <td class="home-score">3</td>
                    <td class="away-score">3</td>
                    <td class="status">FT</td>
                </tr>
            </tbody>
        </table>
    </html>
    """
    
    # Parse results
    results = provider._extract_results_from_html(sample_html)
    
    print(f"\n✓ Parsed {len(results)} results:")
    for result in results:
        print(f"  [{result.fixture_id}] {result.home_team} {result.home_score} - {result.away_score} {result.away_team}")
        print(f"    League: {result.league}, Status: {result.status}")


def demo_rate_limiting():
    """Demonstrate rate limiting."""
    print("\n" + "=" * 60)
    print("Demo 4: Rate Limiting")
    print("=" * 60)
    
    provider = WebScraperProvider(allow_network=False)
    
    print(f"\n✓ Rate limiting configured:")
    print(f"  Requests per minute: {provider.meta.rate_limit_per_minute}")
    print(f"  Minimum interval: {provider._min_request_interval:.2f} seconds")
    print(f"  This ensures respectful scraping that won't overwhelm target sites")


def demo_caching():
    """Demonstrate caching."""
    print("\n" + "=" * 60)
    print("Demo 5: Response Caching")
    print("=" * 60)
    
    provider = WebScraperProvider(allow_network=False)
    
    test_url = "http://example.com/fixtures"
    cache_path = provider._get_cache_path(test_url)
    
    print(f"\n✓ Caching configuration:")
    print(f"  Cache directory: {provider.cache_dir}")
    print(f"  Cache TTL: {provider.meta.refresh_seconds} seconds")
    print(f"  Example cache path: {cache_path.name}")
    print(f"  Caching reduces network requests and respects target servers")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  GFPS Web Scraper Provider - Demo Script".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    demo_basic_usage()
    demo_parsing_fixtures()
    demo_parsing_results()
    demo_rate_limiting()
    demo_caching()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The WebScraperProvider enables GFPS to gather football data from
publicly available websites alongside existing API providers.

Key Features:
  ✓ Configurable CSS selectors for any HTML structure
  ✓ Built-in rate limiting (30 requests/minute)
  ✓ Response caching to minimize requests
  ✓ Graceful error handling
  ✓ Works offline with cached data
  ✓ Integrates seamlessly with existing data pipeline

Usage:
  1. Configure selectors in SCRAPER_CONFIG_PATH JSON file
  2. Set ENABLE_WEB_SCRAPER=1
  3. Set ENABLE_LIVE_NETWORK=1
  4. Run: python -m backend.pipeline_cli ingest_fixtures

For more details, see: docs/web-scraper.md
    """)
    print("=" * 60)


if __name__ == "__main__":
    main()
