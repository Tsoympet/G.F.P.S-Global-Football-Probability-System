# Odds Snapshots

The odds snapshot pipeline stores bookmaker prices over time for CLV analysis and walk‑forward validation.

## Storage
- Table: `odds_snapshots`
- Columns: `provider_id`, `match_id`, `market_id`, `selection_id`, `line`, `odds_decimal`, `captured_at`, `is_live`, `source_confidence`, `raw_payload_hash`
- Append-only with de-duplication: identical odds for the same provider/match/market/selection within `ODDS_SNAPSHOT_DEDUP_SEC` (default 45s) are skipped.

## Scheduler
- Enabled only when an odds provider is configured (`APIFOOTBALL_KEY` or `ODDS_PROVIDER_ENABLED`).
- Captures odds periodically using live state:
  - >30m to kickoff: every 30m
  - ≤30m to kickoff: every 5m
  - ≤5m to kickoff: every 2m
- Live odds are persisted when the provider delivers them.

## Usage
- `record_odds_snapshots(rows)` persists batches.
- `closing_odds(match_id, market_id, selection_id, kickoff)` returns the last price before kickoff.

## Limitations
- When no provider is configured, the scheduler is dormant and CLV features report “needs odds snapshots”.
- Coverage depends on the upstream provider; live odds are only stored when legally available.
