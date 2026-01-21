# GFPS Free Operation Guide

## 💰 Run GFPS with $0/month in API costs

**Good news!** GFPS is designed to operate completely free of charge. You don't need any expensive API subscriptions.

## Quick Start: Zero-Cost Setup

### 1. Configure Your Environment

Copy `.env.example` to `.env` and use these settings:

```bash
# ✅ RECOMMENDED: FREE Operation Mode
ENABLE_FOOTBALL_DATA=1    # FREE - Football-Data.org
ENABLE_OPENLIGADB=1       # FREE - OpenLigaDB for German leagues
ENABLE_API_FOOTBALL=0     # KEEP DISABLED - Expensive premium API
APIFOOTBALL_KEY=          # LEAVE EMPTY - No expensive subscription needed

# Optional: Free API key for Football-Data.org
# Register at: https://www.football-data.org/client/register
FOOTBALL_DATA_API_KEY=    # Optional but FREE
```

### 2. What You Get with Free Data Sources

✅ **OpenFootball CSV** (bundled, no setup)
- Fixtures and results for major leagues
- Offline operation (no network required)
- Zero cost, zero configuration

✅ **Football-Data.org** (free tier)
- Live fixtures and results
- Coverage of major European leagues
- Free API key available
- Rate limit: 10 requests/minute (plenty for most users)
- Cost: **$0/month**

✅ **OpenLigaDB** (no key needed)
- Live scores for Bundesliga
- Free public API
- No registration required
- Cost: **$0/month**

### 3. What You DON'T Get with Free Sources

The only thing you lose by not using API-Football is:
- Real-time bookmaker odds (you can still use model-derived fair odds)
- Some minor leagues coverage

**However:** 
- All predictions still work perfectly
- All features remain functional
- Model-derived odds are available as fallback
- You can scrape odds from public websites using the built-in web scraper

## Comparison: Free vs Premium

| Feature | Free Sources | API-Football Premium |
|---------|-------------|---------------------|
| **Cost** | **$0/month** ✅ | **$50-300/month** ❌ |
| Fixtures | ✅ Yes | ✅ Yes |
| Results | ✅ Yes | ✅ Yes |
| Live Scores | ✅ Yes (OpenLigaDB) | ✅ Yes |
| Major Leagues | ✅ Yes | ✅ Yes |
| Predictions | ✅ Yes | ✅ Yes |
| EV Detection | ✅ Yes (with model odds) | ✅ Yes (with market odds) |
| Bookmaker Odds | ⚠️ Via web scraper | ✅ Yes |
| Minor Leagues | ⚠️ Limited | ✅ Extensive |

## Migrating from Premium API to Free

If you're currently using API-Football and want to save money:

### Step 1: Update Environment Variables

Edit your `.env` file:

```bash
# Remove or empty the expensive API key
APIFOOTBALL_KEY=

# Disable the premium provider
ENABLE_API_FOOTBALL=0

# Enable free providers
ENABLE_FOOTBALL_DATA=1
ENABLE_OPENLIGADB=1

# Optional: Get a free API key
FOOTBALL_DATA_API_KEY=your-free-key-here
```

### Step 2: Restart the Backend

```bash
# Stop the current backend
# Then restart:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Operation

Check that the system is using free providers:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/fixtures
```

You should see fixtures from the free providers.

## Getting a Free Football-Data.org API Key

1. Visit https://www.football-data.org/client/register
2. Fill in your email address
3. You'll receive your free API key instantly
4. Add it to your `.env` file as `FOOTBALL_DATA_API_KEY`
5. Restart the backend

**Benefits:**
- Completely free, no credit card required
- 10 requests per minute (sufficient for most use cases)
- Coverage of major European leagues
- Maintained by the football data community

## Using the Web Scraper for Odds

If you need bookmaker odds without paying for API-Football, use the built-in web scraper:

1. Configure a scraper config file (see [docs/web-scraper.md](web-scraper.md))
2. Enable the scraper: `ENABLE_WEB_SCRAPER=1`
3. Point to your config: `SCRAPER_CONFIG_PATH=/path/to/config.yaml`
4. The scraper will pull odds from publicly available websites

**Note:** Only scrape from sites that allow it in their terms of service.

## FAQ

### Q: Will predictions still be accurate without API-Football?

**A:** Yes! The prediction engine uses historical results to build team strength ratings. The source of fixtures doesn't affect prediction quality. Model-derived odds work just as well as market odds for EV detection.

### Q: Can I still use live scores?

**A:** Yes! OpenLigaDB provides free live scores for Bundesliga. For other leagues, the system falls back to polling Football-Data.org.

### Q: What about odds for value betting?

**A:** The system can generate fair odds from model probabilities. Alternatively, use the web scraper to pull odds from publicly available sources.

### Q: How often is data updated with free sources?

**A:** 
- OpenFootball CSV: Manual refresh (offline snapshot)
- Football-Data.org: Every 6 hours (configurable)
- OpenLigaDB: Every 90 seconds (configurable)

This is sufficient for pre-match analysis and value betting.

### Q: Can I mix free and premium sources?

**A:** Yes, but it's not recommended. If you have a premium subscription, you can enable both, but you're paying for redundant data.

## Troubleshooting

### Issue: No fixtures showing up

**Solution:** 
1. Check that at least one provider is enabled
2. Run the ingestion pipeline: `python -m backend.pipeline_cli ingest_fixtures`
3. Verify the bundled OpenFootball CSV files exist in `backend/sample_data/`

### Issue: "Rate limit exceeded" errors

**Solution:**
1. Reduce polling frequency in `.env`: `STREAMER_INTERVAL_SEC=60`
2. For Football-Data.org, stay under 10 requests/minute
3. Enable caching to reduce API calls

### Issue: Want more leagues

**Solution:**
1. Check if Football-Data.org covers your league (they support 10+ major leagues)
2. Use the web scraper to pull data from league-specific websites
3. Add custom CSV files to `backend/sample_data/` following the OpenFootball format

## Support

If you have questions about free operation:
1. Check the main README.md
2. Review docs/DATA_SOURCES.md
3. Open an issue on GitHub

**Remember:** GFPS was designed from the ground up to work without expensive APIs. Enjoy your cost-free football analytics!
