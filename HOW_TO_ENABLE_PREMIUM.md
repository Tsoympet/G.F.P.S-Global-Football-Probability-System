## Enabling Premium Providers

1. Create a local `.env` file (never commit) and add:
   ```
   GFPS_DATA_MODE=premium-enabled
   APIFOOTBALL_KEY=<your_api_football_key>
   ENABLE_API_FOOTBALL=1
   ```
2. Restart the backend or CLI so the new environment variables are loaded.
3. Premium providers remain optional. If the key is missing or invalid, the ingestion pipeline falls back to free providers automatically.
4. Keys are read from environment variables only; store them encrypted at rest using your OS keyring or secret manager. The repository never persists credentials.
5. To return to free-only mode, unset `GFPS_DATA_MODE` or set it to `free-only` and remove the key from your environment.
