# Anti-Leakage Rules

1. **Temporal ordering**
   - Training data must end strictly before the test window starts.
   - Odds snapshots for CLV/feature calc must be captured **before** decision time or kickoff.

2. **Feature availability**
   - Only use features known at or before the prediction timestamp.
   - No results, post‑match stats, or after‑kickoff odds in test features.

3. **Snapshot discipline**
   - Append-only odds snapshots with de‑duplication in a short window.
   - Closing odds = last price at/before kickoff.

4. **Determinism**
   - Same data + config → identical fold splits and metrics.

5. **Reporting**
   - Surface missing odds/fixtures as data quality warnings.
   - If no odds provider is enabled, CLV metrics are marked “needs odds snapshots.”
