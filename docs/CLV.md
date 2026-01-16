# Closing Line Value (CLV)

## Definitions
- **Closing odds**: last pre‑kickoff price for a selection (`closing_odds(match_id, market_id, selection_id, kickoff)`).
- **CLV (odds space)**: `(odds_at_pick / closing_odds) - 1`
- **CLV (probability space)**: `(1 / closing_odds) - (1 / odds_at_pick)`
- **Beat closing**: `odds_at_pick > closing_odds` (better price than close).

## Schema
Bet journal fields:
- `odds_at_pick`, `closing_odds`, `clv_odds`, `clv_prob`, `snapshot_provider`

## Reporting
- KPIs expose:
  - Average CLV (odds & prob)
  - % bets beating close
  - Samples count
- CLV appears beside ROI to separate skill (price quality) from outcomes.

## Notes
- If odds snapshots are missing, CLV metrics are unavailable and reported as `needs odds snapshots`.
- Direction-sensitive markets should compare implied probabilities when price orientation differs.
