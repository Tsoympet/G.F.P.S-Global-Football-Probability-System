## GFPS Provider Matrix

| Provider | Tier | Data Types | Default Refresh | Reliability | Live | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| OpenFootball CSV | Free (default) | Fixtures, Results | 24h (snapshot) | 0.70 | No | None |
| Football-Data.org | Free (keyed) | Fixtures, Results | 6h | 0.55 | No | Optional API key |
| OpenLigaDB | Free (no key) | Fixtures, Live Events | 90s | 0.35 | Yes | None |
| API-Football | Premium (opt-in) | Fixtures, Results, Events, Odds | 60s | 0.90 | Yes | `APIFOOTBALL_KEY` |
| API-Football Stub | Premium placeholder | Fixtures, Results, Events, Odds | 60s | 0.85 | Yes | `APIFOOTBALL_KEY` |

### Modes
- **free-only** (default): premium providers are ignored even if keys are present.
- **hybrid**: free providers run first; premium providers are used when explicitly enabled.
- **premium-enabled**: premium providers run when a valid key is supplied, with free providers as safety net.
