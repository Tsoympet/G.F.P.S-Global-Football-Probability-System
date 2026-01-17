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

## Future Enhancements

Potential improvements for the web scraper:

- [ ] JavaScript rendering support (Selenium/Playwright)
- [ ] Multi-page pagination support
- [ ] Automatic selector learning/discovery
- [ ] Proxy support for geo-restricted content
- [ ] Captcha handling hooks
- [ ] HTML structure change detection/alerting

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
