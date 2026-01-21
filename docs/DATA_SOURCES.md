# GFPS Data Catalog

This catalog documents the data needed to power match probabilities, where it comes from, and the usage constraints.

## 💰 Cost-Free Operation (Recommended)

**GFPS is designed to operate 100% FREE of charge.** You do NOT need any expensive API subscriptions.

## Required Data
- Fixtures (upcoming matches)
- Results (finished matches)
- Events (goals/cards/substitutions) – optional when available
- Lineups – optional when available
- Odds – optional, only from legal sources

## Providers

| Provider | Type | Coverage | Update Frequency | Auth | Licensing / Usage | Cost |
| --- | --- | --- | --- | --- | --- | --- |
| OpenFootball CSV snapshot (bundled) | ✅ **FREE** / no key | Fixtures & results (sample leagues) | Offline snapshot; manual refresh | None | CC0 / public domain snapshot | **$0/mo** |
| Football-Data.org (free tier) | ✅ **FREE** (keyed) | Fixtures & results | Polling every 6h (configurable) | `FOOTBALL_DATA_API_KEY` optional | Free tier, rate-limited | **$0/mo** |
| OpenLigaDB | ✅ **FREE** / no key | Live scores (Bundesliga + limited) | Polling ~90s | None | Public, attribution required | **$0/mo** |
| API-Football | ❌ **EXPENSIVE PREMIUM** (optional) | Fixtures/results/live/odds | Polling ~60s when enabled | `APIFOOTBALL_KEY` | Commercial; **DISABLED BY DEFAULT** | **$50-300/mo** ⚠️ |
| API-Football stub | Premium (placeholder) | No data until keyed | N/A | `APIFOOTBALL_KEY` | Placeholder for plug-in providers | N/A |

## Notes
- **Default mode is FREE-ONLY**. Premium providers remain disabled until a user opts-in and supplies a key.
- **You DO NOT need API-Football** - the free providers cover all core functionality.
- Live updates use polling with TTL caching and will fall back to cached/offline snapshots if the endpoint is unavailable.
- Odds are optional. When unavailable, the odds abstraction exposes fair odds derived from the model probabilities.
- Respect each provider's terms, rate limits, and attribution rules. No hidden endpoints or scraping are used.

## Migration from Premium to Free

If you're currently using API-Football and want to eliminate costs:

1. Remove or leave empty `APIFOOTBALL_KEY` in your `.env` file
2. Set `ENABLE_API_FOOTBALL=0` in your `.env` file
3. Set `ENABLE_FOOTBALL_DATA=1` to enable free Football-Data.org
4. Set `ENABLE_OPENLIGADB=1` to enable free OpenLigaDB
5. Optional: Get a FREE API key from https://www.football-data.org/client/register
6. Restart the backend

The system will automatically use the bundled OpenFootball CSV data plus any enabled free providers.
