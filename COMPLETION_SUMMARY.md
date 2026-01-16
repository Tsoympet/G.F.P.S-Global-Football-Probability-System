## GFPS Desktop Completion Summary

- Wired all desktop data flows to FastAPI `/predictions`, `/odds`, `/value`, and `/health` with encrypted caching, retry-aware polling, and offline fallbacks.
- Enhanced dashboard, Match Center, and Value Scanner with live probability/xG curves, filters, CSV export, stale indicators, and cached TTL-backed storage.
- Added configurable settings (API endpoint, EV/refresh, cache TTL, offline/manual toggles, theme), secure persistence, and new CI workflows for PR checks plus signed installer builds on release tags.
- Delivered a pluggable, legal ingestion pipeline (open CSV provider + optional API key stub), normalization/quality layers, storage schema for fixtures/results/events/lineups/features, scheduler hooks, feature builder, runnable CLI commands, and updated data catalog/architecture docs.
