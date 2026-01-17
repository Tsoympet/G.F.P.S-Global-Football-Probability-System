# Web Scraper Improvements - Implementation Guide

## Overview

The GFPS Web Scraper has been enhanced with six advanced features that enable production-grade web scraping capabilities. These improvements address common challenges when scraping modern football data websites.

## New Features

### 1. JavaScript Rendering Support (Playwright)

**What it does:** Renders dynamic websites that load content via JavaScript, enabling scraping of modern single-page applications (SPAs) and AJAX-heavy sites.

**When to use:**
- Website content loads after initial page load
- Data is fetched via JavaScript/AJAX calls
- Site uses frameworks like React, Vue, or Angular

**Configuration:**
```json
{
  "use_js_rendering": true,
  "js_wait_time": 3000
}
```

**Requirements:**
```bash
pip install playwright
playwright install chromium
```

**Example:**
```python
from backend.data_providers import WebScraperProvider

config = {
    "use_js_rendering": True,
    "js_wait_time": 3000,
    "fixtures_url": "https://dynamic-sports-site.com/fixtures",
    "selectors": {
        "fixture_container": ".match-card",
        "home_team": ".home .name",
        "away_team": ".away .name"
    }
}

provider = WebScraperProvider(config=config, allow_network=True)
fixtures = list(provider.get_fixtures())
```

---

### 2. Multi-Page Pagination Support

**What it does:** Automatically navigates through multiple pages to collect all available data.

**Types supported:**

#### A. URL Pattern Pagination
For sites with predictable URL patterns:
```json
{
  "pagination": {
    "enabled": true,
    "type": "url_pattern",
    "url_pattern": "?page={page}",
    "max_pages": 5
  }
}
```

Example URLs generated:
- `https://site.com/fixtures?page=1`
- `https://site.com/fixtures?page=2`
- `https://site.com/fixtures?page=3`

#### B. Click-Based Pagination
For sites with "Next" buttons (requires JavaScript):
```json
{
  "use_js_rendering": true,
  "pagination": {
    "enabled": true,
    "type": "click",
    "next_button_selector": "button.next-page",
    "max_pages": 10
  }
}
```

#### C. Infinite Scroll
For sites that load content as you scroll (requires JavaScript):
```json
{
  "use_js_rendering": true,
  "pagination": {
    "enabled": true,
    "type": "scroll",
    "max_pages": 10
  }
}
```

---

### 3. Automatic Selector Learning

**What it does:** Analyzes HTML structure and suggests CSS selectors for common football data patterns.

**Configuration:**
```json
{
  "auto_selector_learning": {
    "enabled": true
  }
}
```

**How it works:**
1. Scraper analyzes the HTML structure
2. Looks for common patterns (`.match`, `.fixture`, `[data-match]`)
3. Suggests selectors in log output
4. You refine suggestions and add to config

**Example output:**
```
INFO: Suggested container selector: .match
INFO: Found potential team selector: .team
```

---

### 4. Proxy Support

**What it does:** Routes requests through a proxy server to bypass geo-restrictions or IP-based rate limits.

**Configuration:**

Basic proxy:
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://proxy.example.com:8080"
  }
}
```

Authenticated proxy:
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

**Use cases:**
- Accessing geo-restricted content
- Rotating IPs to avoid rate limits
- Corporate environments requiring proxy

---

### 5. Captcha Handling Hooks

**What it does:** Detects captcha challenges and provides hooks for custom solving logic.

**Configuration:**
```json
{
  "captcha_detection": {
    "enabled": true,
    "indicators": ["captcha", "recaptcha", "hcaptcha", "cloudflare"]
  }
}
```

**Implementation:**
```python
from backend.data_providers import WebScraperProvider

def my_captcha_solver(url: str) -> str:
    """
    Solve captcha using external service.
    
    Could integrate with:
    - 2captcha.com
    - Anti-Captcha
    - DeathByCaptcha
    - Manual solving queue
    """
    # Your solving logic here
    solved_html = solve_captcha_service(url)
    return solved_html

provider = WebScraperProvider(config=config, allow_network=True)
provider.set_captcha_handler(my_captcha_solver)

# Now captchas will be automatically detected and solved
fixtures = list(provider.get_fixtures())
```

---

### 6. HTML Structure Change Detection

**What it does:** Monitors HTML structure over time and alerts when significant changes occur that might break your selectors.

**Configuration:**
```json
{
  "structure_monitoring": {
    "enabled": true,
    "similarity_threshold": 0.8
  }
}
```

**How it works:**
1. First scrape: Computes structural signature (tag counts, class distribution)
2. Subsequent scrapes: Compares current structure to baseline
3. If similarity < threshold: Logs warning
4. Updates baseline with new structure

**Example alert:**
```
WARNING: HTML structure change detected for https://site.com/fixtures: 
         similarity=0.65, threshold=0.8
```

This helps you proactively update selectors before scraping completely fails.

---

## Complete Example

Here's a real-world configuration using all features:

```json
{
  "fixtures_url": "https://example-sports-site.com/fixtures",
  "results_url": "https://example-sports-site.com/results",
  
  "use_js_rendering": true,
  "js_wait_time": 3000,
  
  "pagination": {
    "enabled": true,
    "type": "url_pattern",
    "url_pattern": "?page={page}",
    "max_pages": 5
  },
  
  "proxy": {
    "enabled": true,
    "server": "http://proxy.example.com:8080",
    "username": "user",
    "password": "pass"
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
    "enabled": true
  },
  
  "selectors": {
    "fixture_container": "div.match-card",
    "fixture_id": "[data-match-id]",
    "home_team": ".team.home .name",
    "away_team": ".team.away .name",
    "kickoff": "time[datetime]",
    "league": ".league-name",
    "season": ".season-year",
    "venue": ".venue-name"
  },
  
  "result_selectors": {
    "home_score": ".score.home",
    "away_score": ".score.away",
    "status": ".match-status"
  }
}
```

## Best Practices

### 1. Start Simple, Add Features as Needed
- Begin with basic HTTP scraping
- Add JavaScript rendering only if content is dynamic
- Enable pagination if you need multiple pages
- Add proxy/captcha handling as obstacles arise

### 2. Test Incrementally
```python
# Test basic scraping first
provider = WebScraperProvider(config=basic_config, allow_network=True)
fixtures = list(provider.get_fixtures())
print(f"Found {len(fixtures)} fixtures")

# Then add features one at a time
# Test JS rendering
# Test pagination
# etc.
```

### 3. Monitor Logs
Enable debug logging to understand what's happening:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. Use Structure Monitoring in Production
This helps catch website changes before users report issues:
```json
{
  "structure_monitoring": {
    "enabled": true,
    "similarity_threshold": 0.8
  }
}
```

### 5. Respect Rate Limits
The scraper has built-in rate limiting (30 req/min by default), but you can adjust:
```python
provider._min_request_interval = 5.0  # 5 seconds between requests
```

## Troubleshooting

### JavaScript Content Not Loading
**Problem:** Data appears empty even with JS rendering enabled.

**Solutions:**
1. Increase `js_wait_time`: `"js_wait_time": 5000`
2. Check if site requires login/cookies
3. Verify selectors in browser dev tools

### Pagination Not Working
**Problem:** Only first page scraped.

**Solutions:**
1. Verify pagination type matches site behavior
2. For click pagination, check next button selector is correct
3. Increase `max_pages` if stopping too early
4. Check logs for pagination errors

### Proxy Connection Fails
**Problem:** Requests timeout or fail with proxy enabled.

**Solutions:**
1. Verify proxy server URL is correct
2. Test proxy connectivity outside Python
3. Check authentication credentials
4. Ensure proxy supports HTTP/HTTPS

### Captcha Not Detected
**Problem:** Captcha present but not detected.

**Solutions:**
1. Add site-specific indicators: `"indicators": ["cloudflare", "your-custom-indicator"]`
2. Check HTML source for captcha-related keywords
3. Verify detection is enabled: `"enabled": true`

## Performance Considerations

### JavaScript Rendering
- **Overhead:** ~2-3 seconds per page
- **Memory:** ~100-200 MB per browser instance
- **Recommendation:** Use only when necessary

### Pagination
- **Time:** Linear with number of pages
- **Recommendation:** Set reasonable `max_pages` limit

### Proxy
- **Latency:** Adds ~100-500ms per request
- **Recommendation:** Use only when needed (geo-restrictions)

## Migration from Old Scraper

Existing configurations work without changes. To adopt new features:

1. **Add gradually:** Start with one feature at a time
2. **Test thoroughly:** Verify data quality after each change
3. **Monitor logs:** Watch for warnings/errors
4. **Document changes:** Keep notes on what works

## Support & Resources

- **Documentation:** `docs/web-scraper.md`
- **Demo Script:** `scripts/demo_web_scraper_advanced.py`
- **Example Config:** `backend/sample_data/scraper-config-example.json`
- **Tests:** `backend/tests/test_web_scraper.py`

## Security Notes

1. **Never commit credentials:** Use environment variables for proxy auth
2. **Validate sources:** Only scrape trusted websites
3. **Check ToS:** Ensure scraping is permitted
4. **Rate limiting:** Respect server resources
5. **Error handling:** All features have graceful fallbacks

## Future Enhancements

Potential improvements for future releases:
- Auto-retry with exponential backoff
- Distributed scraping across multiple machines
- Screenshot capture on errors
- AJAX request interception
- Cookie/session management
- WebDriver manager integration

---

**Last Updated:** 2026-01-17  
**Version:** 1.0  
**Status:** Production Ready ✅
