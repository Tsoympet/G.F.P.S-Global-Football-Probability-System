# GFPS Data Catalog

This catalog documents the data needed to power match probabilities, where it comes from, and the usage constraints.

## Required Data
- Fixtures (upcoming matches)
- Results (finished matches)
- Events (goals/cards/substitutions) – optional when available
- Lineups – optional when available
- Odds – optional, only from legal sources

## Providers

| Provider | Type | Coverage | Update Frequency | Auth | Licensing / Usage |
| --- | --- | --- | --- | --- | --- |
| OpenFootball CSV snapshot (bundled) | Free / no key | Fixtures & results (sample leagues) | Offline snapshot; manual refresh | None | CC0 / public domain snapshot |
| Football-Data.org (free tier) | Free (keyed) | Fixtures & results | Polling every 6h (configurable) | `FOOTBALL_DATA_API_KEY` optional | Free tier, rate-limited |
| OpenLigaDB | Free / no key | Live scores (Bundesliga + limited) | Polling ~90s | None | Public, attribution required |
| API-Football | Premium (optional) | Fixtures/results/live/odds | Polling ~60s when enabled | `APIFOOTBALL_KEY` | Commercial; disabled by default |
| API-Football stub | Premium (placeholder) | No data until keyed | N/A | `APIFOOTBALL_KEY` | Placeholder for plug-in providers |

## Notes
- Default mode is **free-only**. Premium providers remain disabled until a user opts-in and supplies a key.
- Live updates use polling with TTL caching and will fall back to cached/offline snapshots if the endpoint is unavailable.
- Odds are optional. When unavailable, the odds abstraction exposes fair odds derived from the model probabilities.
- Respect each provider’s terms, rate limits, and attribution rules. No hidden endpoints or scraping are used.
