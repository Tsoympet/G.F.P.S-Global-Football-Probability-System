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
| OpenFootball CSV snapshot (bundled) | No-key | Premier League sample fixtures/results | Static snapshot; refresh manually when new snapshot added | None | Open data / public domain snapshot used for offline-safe ingestion |
| API-Football (stubbed) | Key-based (optional) | Full fixtures/results/live | As per provider limits; typically minute-level | API key | Commercial; requires valid license. Disabled by default; plug-in only. |

## Notes
- Live updates are only supported when a provider explicitly allows unauthenticated live access. The default OpenFootball snapshot is offline-only.
- Odds are treated as optional. The system will compute “fair odds” internally from probabilities when external odds are absent.
- Respect each provider’s terms, rate limits, and attribution rules. No hidden endpoints or scraping are used.
