# Walk-Forward Validation

## Concept
Train on past data, test on the immediately following window, roll forward, repeat. Prevents look‑ahead and shows stability over time.

## Configuration
- `train_window_days` (default 180)
- `test_window_days` (default 30)
- `step_days` (default 30)

## API
- `build_walk_forward_folds(timestamps, cfg)` → fold boundaries and indices
- `walk_forward_validate(dataset, cfg, fit, predict, score)` → runs folds with hooks:
  - `fit(train_rows)` -> model
  - `predict(model, test_rows)` -> predictions
  - `score(preds, test_rows)` -> metrics (log loss/Brier/ROI/CLV as needed)

## Metrics
Per fold and aggregated:
- Log loss, Brier score, calibration/error metrics
- ROI / yield / drawdown (if odds + outcomes exist)
- CLV (when odds snapshots are present)

## Output
- Fold windows, train/test sizes, metrics per fold
- Deterministic splits (same data + config → same folds)

## Limitations
- Requires each row to carry a `timestamp`/`kickoff`
- No future data may leak into a fold: training ends strictly before test starts
