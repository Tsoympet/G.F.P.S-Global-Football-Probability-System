## Legal & Compliance Guardrails

- Default operation uses open data only (OpenFootball CSV, Football-Data.org free tier, OpenLigaDB). Premium feeds are disabled until a user provides keys and opts-in.
- No scraping or paywall bypassing. All HTTP calls target documented public endpoints with published rate limits.
- Odds are optional. When bookmaker odds are absent, GFPS exposes fair odds derived from model probabilities rather than fabricating market prices.
- API keys live in environment variables or external secret stores; they are never committed to the repository.
- Attribution: follow each provider’s licensing notes (CC0 for OpenFootball, provider-specific terms for others). Remove or disable any provider if terms change.
