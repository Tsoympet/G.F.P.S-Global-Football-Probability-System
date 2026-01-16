from datetime import datetime, timedelta, timezone

from backend.evaluation.walk_forward import (
    WalkForwardConfig,
    build_walk_forward_folds,
    walk_forward_validate,
)


def test_fold_splits_are_ordered_and_leak_free():
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    timestamps = [base + timedelta(days=day) for day in range(0, 10, 2)]
    cfg = WalkForwardConfig(train_window_days=4, test_window_days=2, step_days=2)
    folds = build_walk_forward_folds(timestamps, cfg)
    assert folds, "Expected folds to be produced"
    for fold in folds:
        assert fold.train_end <= fold.test_start
        for idx in fold.train_indices:
            assert fold.train_start <= timestamps[idx] < fold.train_end
        for idx in fold.test_indices:
            assert fold.test_start <= timestamps[idx] < fold.test_end


def test_walk_forward_determinism():
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    dataset = [{"timestamp": base + timedelta(days=day), "y": day % 2} for day in range(0, 8)]
    cfg = WalkForwardConfig(train_window_days=3, test_window_days=2, step_days=2)

    def fit(train):
        return {"mean": sum(r["y"] for r in train) / len(train)}

    def predict(model, test):
        return [{"pred": model["mean"], "y": r["y"]} for r in test]

    def score(preds, test):
        return {"logloss": sum(abs(p["pred"] - r["y"]) for p, r in zip(preds, test))}

    first = walk_forward_validate(dataset, cfg, fit, predict, score)
    second = walk_forward_validate(dataset, cfg, fit, predict, score)
    assert first == second
