#!/usr/bin/env python3
"""
Demo script showing the advanced features of WebScraperProvider.

This script demonstrates:
1. JavaScript rendering support
2. Multi-page pagination (URL pattern, click, scroll)
3. Automatic selector learning
4. Proxy configuration
5. Captcha handling hooks
6. HTML structure change detection
"""

from backend.data_providers import WebScraperProvider


def demo_javascript_rendering():
    """Demonstrate JavaScript rendering capability."""
    print("=" * 60)
    print("Demo 1: JavaScript Rendering Support")
    print("=" * 60)
    
    config = {
        "use_js_rendering": True,
        "js_wait_time": 3000,
        "fixtures_url": "http://example.com/fixtures",
        "selectors": {
            "fixture_container": ".match",
            "home_team": ".home",
            "away_team": ".away",
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    print(f"\n✓ JavaScript rendering: {provider.use_js_rendering}")
    print(f"  Wait time: {provider.config.get('js_wait_time')}ms")
    print(f"  Playwright available: {provider.use_js_rendering}")
    print(f"\nNote: Install Playwright with 'pip install playwright' and")
    print(f"      'playwright install chromium' to enable this feature")


def demo_pagination():
    """Demonstrate pagination support."""
    print("\n" + "=" * 60)
    print("Demo 2: Multi-Page Pagination Support")
    print("=" * 60)
    
    # URL pattern pagination
    config_url = {
        "fixtures_url": "http://example.com/fixtures",
        "pagination": {
            "enabled": True,
            "type": "url_pattern",
            "url_pattern": "?page={page}",
            "max_pages": 5
        },
        "selectors": {
            "fixture_container": ".match"
        }
    }
    
    print("\n1. URL Pattern Pagination:")
    print(f"   Type: {config_url['pagination']['type']}")
    print(f"   Pattern: {config_url['pagination']['url_pattern']}")
    print(f"   Max pages: {config_url['pagination']['max_pages']}")
    
    # Click-based pagination
    config_click = {
        "use_js_rendering": True,
        "fixtures_url": "http://example.com/fixtures",
        "pagination": {
            "enabled": True,
            "type": "click",
            "next_button_selector": "button.next-page",
            "max_pages": 10
        }
    }
    
    print("\n2. Click-Based Pagination (requires JS):")
    print(f"   Type: {config_click['pagination']['type']}")
    print(f"   Next button: {config_click['pagination']['next_button_selector']}")
    print(f"   Max pages: {config_click['pagination']['max_pages']}")
    
    # Infinite scroll
    config_scroll = {
        "use_js_rendering": True,
        "fixtures_url": "http://example.com/fixtures",
        "pagination": {
            "enabled": True,
            "type": "scroll",
            "max_pages": 10
        }
    }
    
    print("\n3. Infinite Scroll (requires JS):")
    print(f"   Type: {config_scroll['pagination']['type']}")
    print(f"   Max scrolls: {config_scroll['pagination']['max_pages']}")


def demo_selector_learning():
    """Demonstrate automatic selector learning."""
    print("\n" + "=" * 60)
    print("Demo 3: Automatic Selector Learning")
    print("=" * 60)
    
    config = {
        "auto_selector_learning": {
            "enabled": True
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    # Sample HTML
    sample_html = """
    <html>
        <body>
            <div class="match">
                <span class="home">Team A</span>
                <span class="away">Team B</span>
            </div>
            <div class="match">
                <span class="home">Team C</span>
                <span class="away">Team D</span>
            </div>
        </body>
    </html>
    """
    
    print("\n✓ Selector learning enabled")
    print("  Analyzing HTML structure...")
    suggestions = provider._learn_selectors(sample_html)
    
    if suggestions:
        print("\n  Suggested selectors:")
        for key, value in suggestions.items():
            print(f"    {key}: {value}")
    else:
        print("  No specific suggestions (check logs for details)")


def demo_proxy_support():
    """Demonstrate proxy configuration."""
    print("\n" + "=" * 60)
    print("Demo 4: Proxy Support for Geo-Restricted Content")
    print("=" * 60)
    
    config = {
        "fixtures_url": "http://example.com/fixtures",
        "proxy": {
            "enabled": True,
            "server": "http://proxy.example.com:8080",
            "username": "myuser",
            "password": "mypass"
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    print("\n✓ Proxy configured:")
    print(f"  Enabled: {provider.config['proxy']['enabled']}")
    print(f"  Server: {provider.config['proxy']['server']}")
    print(f"  Authentication: {'Yes' if provider.config['proxy']['username'] else 'No'}")
    print("\nNote: Proxy settings work with both basic HTTP requests and")
    print("      JavaScript rendering via Playwright")


def demo_captcha_handling():
    """Demonstrate captcha handling hooks."""
    print("\n" + "=" * 60)
    print("Demo 5: Captcha Handling Hooks")
    print("=" * 60)
    
    config = {
        "captcha_detection": {
            "enabled": True,
            "indicators": ["captcha", "recaptcha", "hcaptcha", "cloudflare"]
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    # Define a custom captcha handler
    def custom_captcha_solver(url: str) -> str:
        """
        Custom captcha solving logic.
        
        In production, this could integrate with:
        - 2captcha.com
        - Anti-Captcha
        - DeathByCaptcha
        - Manual solving queue
        """
        print(f"\n  → Captcha detected at: {url}")
        print("  → Calling captcha solving service...")
        print("  → Captcha solved!")
        return "<html><!-- solved captcha --></html>"
    
    # Register the handler
    provider.set_captcha_handler(custom_captcha_solver)
    
    print("\n✓ Captcha detection enabled")
    print(f"  Indicators: {', '.join(provider.config['captcha_detection']['indicators'])}")
    print("  Handler registered: ✓")
    
    # Test detection
    html_with_captcha = "<html><body><div class='g-recaptcha'></div></body></html>"
    detected = provider._detect_captcha(html_with_captcha)
    print(f"\n  Testing detection on sample HTML: {'Detected ✓' if detected else 'Not detected'}")


def demo_structure_monitoring():
    """Demonstrate HTML structure change detection."""
    print("\n" + "=" * 60)
    print("Demo 6: HTML Structure Change Detection")
    print("=" * 60)
    
    config = {
        "structure_monitoring": {
            "enabled": True,
            "similarity_threshold": 0.8
        }
    }
    
    provider = WebScraperProvider(config=config, allow_network=False)
    
    print("\n✓ Structure monitoring enabled")
    print(f"  Similarity threshold: {provider.config['structure_monitoring']['similarity_threshold']}")
    
    # Simulate structure changes
    url = "http://example.com/fixtures"
    
    html_v1 = """
    <html><body>
        <div class="match"><span class="team">A</span></div>
        <div class="match"><span class="team">B</span></div>
    </body></html>
    """
    
    html_v2 = """
    <html><body>
        <table class="matches">
            <tr><td>Team A</td></tr>
            <tr><td>Team B</td></tr>
        </table>
    </body></html>
    """
    
    print("\n  First scrape (baseline):")
    changed1 = provider._detect_structure_change(url, html_v1)
    print(f"    Change detected: {changed1} (expected: False)")
    
    print("\n  Second scrape (same structure):")
    changed2 = provider._detect_structure_change(url, html_v1)
    print(f"    Change detected: {changed2} (expected: False)")
    
    print("\n  Third scrape (different structure):")
    changed3 = provider._detect_structure_change(url, html_v2)
    print(f"    Change detected: {changed3}")
    print("    → Alert would be logged to help update selectors!")


def demo_complete_example():
    """Show a complete configuration with all features."""
    print("\n" + "=" * 60)
    print("Demo 7: Complete Configuration Example")
    print("=" * 60)
    
    config = {
        "fixtures_url": "https://example-sports-site.com/fixtures",
        "results_url": "https://example-sports-site.com/results",
        
        # JavaScript rendering
        "use_js_rendering": True,
        "js_wait_time": 3000,
        
        # Pagination
        "pagination": {
            "enabled": True,
            "type": "url_pattern",
            "url_pattern": "?page={page}",
            "max_pages": 5
        },
        
        # Proxy
        "proxy": {
            "enabled": True,
            "server": "http://proxy.example.com:8080"
        },
        
        # Captcha detection
        "captcha_detection": {
            "enabled": True,
            "indicators": ["captcha", "recaptcha"]
        },
        
        # Structure monitoring
        "structure_monitoring": {
            "enabled": True,
            "similarity_threshold": 0.8
        },
        
        # Auto-learning
        "auto_selector_learning": {
            "enabled": True
        },
        
        # Selectors
        "selectors": {
            "fixture_container": "div.match-card",
            "fixture_id": "[data-match-id]",
            "home_team": ".team.home .name",
            "away_team": ".team.away .name",
            "kickoff": "time[datetime]",
            "league": ".league-name",
            "season": "2024"
        }
    }
    
    print("\n✓ Complete configuration combining all features:")
    print(f"  JavaScript rendering: {config['use_js_rendering']}")
    print(f"  Pagination: {config['pagination']['type']} ({config['pagination']['max_pages']} pages)")
    print(f"  Proxy: {config['proxy']['enabled']}")
    print(f"  Captcha detection: {config['captcha_detection']['enabled']}")
    print(f"  Structure monitoring: {config['structure_monitoring']['enabled']}")
    print(f"  Auto-learning: {config['auto_selector_learning']['enabled']}")
    
    print("\n  This configuration provides:")
    print("    • Dynamic content rendering")
    print("    • Multi-page data collection")
    print("    • Geo-restriction bypass")
    print("    • Automated captcha handling")
    print("    • Proactive structure change alerts")
    print("    • Intelligent selector suggestions")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  GFPS Web Scraper - Advanced Features Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    demo_javascript_rendering()
    demo_pagination()
    demo_selector_learning()
    demo_proxy_support()
    demo_captcha_handling()
    demo_structure_monitoring()
    demo_complete_example()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The WebScraperProvider now includes advanced features for
production-grade web scraping:

✓ JavaScript Rendering (Playwright)
  - Scrape dynamic sites with client-side rendering
  - Full browser automation support
  - Configurable wait times for content loading

✓ Multi-Page Pagination
  - URL pattern pagination for predictable URLs
  - Click-based pagination for "Next" buttons
  - Infinite scroll support for lazy-loaded content

✓ Automatic Selector Learning
  - Analyzes HTML structure
  - Suggests selectors based on patterns
  - Reduces manual configuration effort

✓ Proxy Support
  - Bypass geo-restrictions
  - Rotate IPs for rate limit avoidance
  - Supports authenticated proxies

✓ Captcha Handling
  - Automatic captcha detection
  - Custom handler hooks for solving
  - Integration-ready with captcha services

✓ Structure Change Detection
  - Monitors HTML structure over time
  - Alerts when significant changes occur
  - Helps maintain selector accuracy

All features work together seamlessly and can be configured
independently based on your needs.

For detailed documentation, see: docs/web-scraper.md
    """)
    print("=" * 60)


if __name__ == "__main__":
    main()
