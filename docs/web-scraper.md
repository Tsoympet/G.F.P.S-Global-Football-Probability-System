# Web Scraper Data Provider

The Web Scraper Provider enables GFPS to gather football data from publicly available websites using HTML scraping. This complements the existing API-based data providers and allows integration with sources that don't offer APIs.

## Overview

The `WebScraperProvider` is a configurable data provider that:
- Scrapes football fixtures and results from HTML pages
- Uses CSS selectors to extract data from web pages
- Includes rate limiting to be a respectful web citizen
- Caches responses to minimize requests
- Works alongside existing API providers in the data ingestion pipeline

## Features

- **Configurable CSS Selectors**: Define selectors for each data field
- **Rate Limiting**: Automatic throttling to avoid overwhelming target sites
- **Response Caching**: Caches HTML responses to reduce network requests
- **Error Handling**: Gracefully handles malformed HTML and network errors
- **Respectful User-Agent**: Identifies itself as GFPS scraper
- **Network Toggle**: Can be disabled for offline operation

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Enable web scraper
ENABLE_WEB_SCRAPER=1

# Enable network requests (required for scraper to fetch data)
ENABLE_LIVE_NETWORK=1

# Optional: Path to custom scraper configuration file
SCRAPER_CONFIG_PATH=/path/to/scraper-config.json
```

### Scraper Configuration File

Create a JSON configuration file that defines:
1. URLs to scrape
2. CSS selectors for extracting data

Example configuration (`scraper-config.json`):

```json
{
  "fixtures_url": "https://example-sports-site.com/upcoming-matches",
  "results_url": "https://example-sports-site.com/results",
  
  "selectors": {
    "fixture_container": "div.match-row",
    "fixture_id": "[data-match-id]",
    "home_team": "span.team.home",
    "away_team": "span.team.away",
    "kickoff": "time[datetime]",
    "league": "div.competition-name",
    "season": "span.season-year",
    "venue": "span.venue-name"
  },
  
  "result_selectors": {
    "home_score": "span.score.home",
    "away_score": "span.score.away",
    "status": "span.match-status"
  }
}
```

### Selector Reference

#### Required Selectors

These selectors are used to extract fixture data:

| Selector | Description | Example |
|----------|-------------|---------|
| `fixture_container` | Container element for each match | `div.match`, `tr.fixture-row` |
| `fixture_id` | Unique identifier for the match | `[data-id]`, `.match-id` |
| `home_team` | Home team name | `.home-team`, `td.home` |
| `away_team` | Away team name | `.away-team`, `td.away` |
| `league` | League/competition name | `.league`, `.competition` |
| `season` | Season identifier | `.season`, `[data-season]` |
| `kickoff` | Match date/time | `time`, `.datetime` |

#### Optional Selectors

| Selector | Description | Default |
|----------|-------------|---------|
| `venue` | Stadium/venue name | Empty string |

#### Result-Specific Selectors

For scraping completed match results:

| Selector | Description | Example |
|----------|-------------|---------|
| `home_score` | Home team score | `.score.home`, `td.home-score` |
| `away_score` | Away team score | `.score.away`, `td.away-score` |
| `status` | Match status (FT, HT, etc.) | `.status`, `[data-status]` |

## Defining targets for a live-style feed (bookmakers/tipsters)

Until API data is available, scrape the smallest set of HTML fields that lets the probability engine behave like a live feed. Capture:

| Data point | Why it matters | Typical selector examples |
|------------|----------------|---------------------------|
| Fixture identity (`fixture_id`, `home_team`, `away_team`, `kickoff`) | Links odds to the correct match | `[data-match-id]`, `.team.home`, `.team.away`, `time[datetime]` |
| Match status (`status`, `clock`, `period`) | Enables live probability updates and bet settlement logic | `.match-status`, `.clock`, `[data-period]` |
| Market name (`market`, e.g. `1x2`, `over_under_2_5`, `btts`) | Groups prices under the right market for bookers/tipsters | `.market-name`, `[data-market]` |
| Selection labels (`home`, `draw`, `away`, `over`, `under`, `yes`, `no`) | Ties each price to the correct outcome | `.selection-name`, `[data-outcome]` |
| Odds/price (`decimal_odds`) | Core input to implied probability | `.price`, `[data-odds]`, `.odds-decimal` |
| Line/handicap (`line`) | Needed for totals/spreads | `.line`, `[data-line]` |
| Bookmaker/source (`source`) | Attribution and conflict resolution | `.bookmaker`, `[data-source]` |
| Last updated (`last_updated`) | Lets engine ignore stale prices | `time.last-updated`, `[data-updated-at]` |

Map these selectors in your `selectors` section using custom keys (e.g., `market_selector`, `price_selector`) and read them in your downstream parsing logic. Keep `refresh_seconds` short (e.g., 30–60s) in `data_providers.settings` for a live-like cadence, and enable `ENABLE_LIVE_NETWORK=1` plus `ENABLE_WEB_SCRAPER=1`.

## Usage

### With Pipeline CLI

The web scraper is automatically included when you run the ingestion pipeline:

```bash
# Ingest fixtures from all enabled providers (including web scraper)
python -m backend.pipeline_cli ingest_fixtures

# The scraper will be used if ENABLE_WEB_SCRAPER=1
```

### Programmatic Usage

```python
from pathlib import Path
from backend.data_providers import WebScraperProvider

# Option 1: Load config from file
config_path = Path("/path/to/scraper-config.json")
provider = WebScraperProvider(
    config_path=config_path,
    allow_network=True
)

# Option 2: Provide config directly
config = {
    "fixtures_url": "https://example.com/fixtures",
    "selectors": {
        "fixture_container": ".match",
        "fixture_id": "[data-id]",
        "home_team": ".home",
        "away_team": ".away",
        "kickoff": "time",
        "league": ".league",
        "season": ".season"
    }
}
provider = WebScraperProvider(config=config, allow_network=True)

# Fetch fixtures
for fixture in provider.get_fixtures():
    print(f"{fixture.home_team} vs {fixture.away_team}")

# Fetch results
for result in provider.get_results():
    print(f"{result.home_team} {result.home_score} - {result.away_score} {result.away_team}")
```

## CSS Selector Tips

### Finding the Right Selectors

1. **Open Developer Tools**: In your browser, right-click on the page and select "Inspect"
2. **Find the Container**: Locate the HTML element that contains one match/fixture
3. **Identify Unique Classes/IDs**: Look for classes or IDs that uniquely identify the container
4. **Test Your Selector**: Use browser console to test: `document.querySelectorAll('.your-selector')`

### Common Selector Patterns

```css
/* By class */
.match-container

/* By ID */
#fixture-12345

/* By attribute */
[data-match-id]

/* By tag and class */
div.fixture

/* Nested elements */
.match .home-team

/* Nth child */
tr:nth-child(2)

/* Multiple classes */
.match.upcoming

/* Attribute contains */
[class*="fixture"]
```

## Caching

The scraper caches HTML responses in `backend/cache/` directory:
- Cache TTL is configured via `refresh_seconds` (default: 3600 seconds / 1 hour)
- Old cache entries are automatically used if within TTL
- Manual cache clearing: Delete files from `backend/cache/`

## Rate Limiting

The scraper automatically rate-limits requests:
- Default: 30 requests per minute (2 seconds between requests)
- Configurable via `rate_limit_per_minute` in provider metadata
- Prevents overwhelming target websites

## Best Practices

### Legal and Ethical Considerations

1. **Check Terms of Service**: Ensure the website allows scraping
2. **Respect robots.txt**: Check if the site prohibits automated access
3. **Use Public Data Only**: Only scrape publicly available information
4. **Rate Limit Appropriately**: Don't overwhelm the target server
5. **Cache Responses**: Minimize repeated requests

### Technical Best Practices

1. **Test Selectors First**: Verify selectors work before full deployment
2. **Handle Missing Data**: Expect fields to be missing occasionally
3. **Monitor Logs**: Check logs for scraping errors
4. **Update Selectors**: Website changes may break selectors
5. **Use Multiple Providers**: Don't rely solely on scraped data

## Troubleshooting

### No Fixtures/Results Returned

**Check:**
- `ENABLE_WEB_SCRAPER=1` is set
- `ENABLE_LIVE_NETWORK=1` is set
- URLs in config are correct and accessible
- CSS selectors match the actual HTML structure

**Debug:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check scraper is registered
python -c "from backend.ingestion_pipeline import _build_registry; \
           r = _build_registry(); \
           print([p.meta.name for p in r.active(data_types={'fixtures'})])"
```

### Selectors Don't Match

**Test selectors in browser console:**
```javascript
// Test container selector
document.querySelectorAll('.match-container')

// Test nested selector
document.querySelector('.match-container .home-team').textContent
```

### Rate Limiting Too Aggressive

**Adjust in code:**
```python
provider = WebScraperProvider(config=config, allow_network=True)
provider._min_request_interval = 5.0  # 5 seconds between requests
```

### Cache Issues

**Clear cache:**
```bash
rm -rf backend/cache/scraper_*.html
```

## Integration with Existing Providers

The web scraper works alongside other providers in the data pipeline:

**Priority Order** (lower number = higher priority):
1. OpenFootball CSV (priority 5)
2. Football-Data.org (priority 15)
3. **Web Scraper (priority 20)** ← Your scraper
4. OpenLigaDB (priority 25)
5. API-Football Premium (priority 70)

Data from higher-priority providers is preferred during deduplication.

## Security Considerations

1. **No Credentials Required**: Scraper doesn't need API keys
2. **Network-Only**: Only accesses public web pages
3. **User-Agent Identification**: Clearly identifies itself
4. **Respects Rate Limits**: Built-in throttling
5. **Error Isolation**: Scraper errors don't affect other providers

## Example Configurations

### Example 1: Simple Table-Based Layout

```json
{
  "fixtures_url": "https://example.com/fixtures.html",
  "selectors": {
    "fixture_container": "table.fixtures tbody tr",
    "fixture_id": "td:nth-child(1)",
    "home_team": "td:nth-child(2)",
    "away_team": "td:nth-child(3)",
    "kickoff": "td:nth-child(4)",
    "league": "td:nth-child(5)",
    "season": "2024"
  }
}
```

### Example 2: Card-Based Layout

```json
{
  "fixtures_url": "https://example.com/matches",
  "selectors": {
    "fixture_container": "div.match-card",
    "fixture_id": "[data-match-id]",
    "home_team": ".team.home .team-name",
    "away_team": ".team.away .team-name",
    "kickoff": ".match-time[datetime]",
    "league": ".league-badge img[alt]",
    "season": "2024",
    "venue": ".venue-info"
  }
}
```

## Advanced Features

### JavaScript Rendering Support

The web scraper now supports JavaScript rendering using Playwright, which enables scraping of dynamic websites that load content via JavaScript.

**Configuration:**

```json
{
  "use_js_rendering": true,
  "js_wait_time": 2000,
  "fixtures_url": "https://example.com/fixtures",
  "selectors": {
    "fixture_container": ".match"
  }
}
```

**Requirements:**
- Install Playwright: `pip install playwright`
- Install browser: `playwright install chromium`

### Multi-Page Pagination Support

The scraper supports three types of pagination:

#### 1. URL Pattern Pagination

For sites with predictable URL patterns (e.g., `/fixtures?page=1`, `/fixtures?page=2`):

```json
{
  "fixtures_url": "https://example.com/fixtures",
  "pagination": {
    "enabled": true,
    "type": "url_pattern",
    "url_pattern": "?page={page}",
    "max_pages": 5
  }
}
```

#### 2. Click-Based Pagination

For sites with "Next" buttons (requires JavaScript rendering):

```json
{
  "use_js_rendering": true,
  "fixtures_url": "https://example.com/fixtures",
  "pagination": {
    "enabled": true,
    "type": "click",
    "next_button_selector": "button.next-page",
    "max_pages": 10
  }
}
```

#### 3. Infinite Scroll

For sites that load content as you scroll (requires JavaScript rendering):

```json
{
  "use_js_rendering": true,
  "fixtures_url": "https://example.com/fixtures",
  "pagination": {
    "enabled": true,
    "type": "scroll",
    "max_pages": 10
  }
}
```

### Proxy Support

For accessing geo-restricted content or avoiding rate limits:

```json
{
  "proxy": {
    "enabled": true,
    "server": "http://proxy.example.com:8080",
    "username": "user",
    "password": "pass"
  }
}
```

**Note:** Proxy credentials are optional and only needed for authenticated proxies.

### Captcha Handling

The scraper can detect captchas and call custom handlers:

**Configuration:**

```json
{
  "captcha_detection": {
    "enabled": true,
    "indicators": ["captcha", "recaptcha", "hcaptcha", "cloudflare"]
  }
}
```

**Usage:**

```python
from backend.data_providers import WebScraperProvider

def my_captcha_solver(url: str) -> str:
    """Custom captcha solving logic."""
    # Your captcha solving code here
    # Could integrate with services like 2captcha, Anti-Captcha, etc.
    return solved_html

provider = WebScraperProvider(config=config, allow_network=True)
provider.set_captcha_handler(my_captcha_solver)
```

### HTML Structure Change Detection

Monitor for website structure changes that might break selectors:

```json
{
  "structure_monitoring": {
    "enabled": true,
    "similarity_threshold": 0.8
  }
}
```

When the HTML structure changes significantly (similarity < threshold), a warning is logged. This helps you proactively update selectors before scraping fails completely.

### Automatic Selector Learning

The scraper can suggest selectors based on common patterns:

```json
{
  "auto_selector_learning": {
    "enabled": true
  }
}
```

When enabled, the scraper analyzes HTML and logs suggested selectors for common football data patterns (matches, teams, scores, etc.). Check logs for suggestions.

## Complete Configuration Example

```json
{
  "fixtures_url": "https://example.com/fixtures",
  "results_url": "https://example.com/results",
  
  "use_js_rendering": true,
  "js_wait_time": 3000,
  
  "pagination": {
    "enabled": true,
    "type": "url_pattern",
    "url_pattern": "?page={page}",
    "max_pages": 5
  },
  
  "proxy": {
    "enabled": false,
    "server": "",
    "username": "",
    "password": ""
  },
  
  "captcha_detection": {
    "enabled": true,
    "indicators": ["captcha", "recaptcha", "hcaptcha"]
  },
  
  "structure_monitoring": {
    "enabled": true,
    "similarity_threshold": 0.8
  },
  
  "auto_selector_learning": {
    "enabled": false
  },
  
  "selectors": {
    "fixture_container": "div.match-card",
    "fixture_id": "[data-match-id]",
    "home_team": ".team.home .team-name",
    "away_team": ".team.away .team-name",
    "kickoff": "time[datetime]",
    "league": ".league-name",
    "season": "2024",
    "venue": ".venue-name"
  },
  
  "result_selectors": {
    "home_score": ".score.home",
    "away_score": ".score.away",
    "status": ".match-status"
  }
}
```

## Implemented Features

The following features are now fully implemented:

- [x] JavaScript rendering support (Playwright)
- [x] Multi-page pagination support (URL pattern, click, scroll)
- [x] Automatic selector learning/discovery
- [x] Proxy support for geo-restricted content
- [x] Captcha handling hooks
- [x] HTML structure change detection/alerting

## Support

For issues with the web scraper:
1. Check this documentation
2. Review logs for error messages
3. Test selectors in browser developer tools
4. Open an issue on GitHub with sample HTML

## Related Documentation

- [Data Providers Overview](./data-providers.md)
- [Ingestion Pipeline](./ingestion-pipeline.md)
- [Provider Registry](./provider-registry.md)
