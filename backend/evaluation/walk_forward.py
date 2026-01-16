"""Walk-forward validation utilities with anti-lookahead safeguards."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class WalkForwardConfig:
    train_window_days: int = 180
    test_window_days: int = 30
    step_days: int = 30


@dataclass(frozen=True)
class WalkForwardFold:
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_indices: List[int]
    test_indices: List[int]


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None
    return None


def build_walk_forward_folds(timestamps: List[datetime], config: WalkForwardConfig) -> List[WalkForwardFold]:
    if not timestamps:
        return []
    sorted_idx = sorted(enumerate(timestamps), key=lambda t: t[1])
    earliest = sorted_idx[0][1]
    folds: List[WalkForwardFold] = []
    cursor = earliest
    train_delta = timedelta(days=config.train_window_days)
    test_delta = timedelta(days=config.test_window_days)
    step_delta = timedelta(days=config.step_days)

    while True:
        train_start = cursor
        train_end = train_start + train_delta
        test_start = train_end
        test_end = test_start + test_delta
        train_indices = [idx for idx, ts in sorted_idx if train_start <= ts < train_end]
        test_indices = [idx for idx, ts in sorted_idx if test_start <= ts < test_end]
        if not test_indices:
            break
        folds.append(
            WalkForwardFold(
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                train_indices=train_indices,
                test_indices=test_indices,
            )
        )
        cursor = cursor + step_delta
    return folds


def walk_forward_validate(
    dataset: List[Mapping[str, Any]],
    config: WalkForwardConfig,
    fit_model: Callable[[List[Mapping[str, Any]]], Any],
    predict: Callable[[Any, List[Mapping[str, Any]]], List[Mapping[str, Any]]],
    score: Callable[[List[Mapping[str, Any]], List[Mapping[str, Any]]], Mapping[str, float]],
) -> Dict[str, Any]:
    """
    Generic walk-forward runner. `dataset` rows must contain a `timestamp` field.
    """
    timestamps = []
    for row in dataset:
        ts = _parse_timestamp(row.get("timestamp") or row.get("kickoff"))
        if ts is None:
            continue
        timestamps.append(ts)
    if len(timestamps) != len(dataset):
        raise ValueError("Every dataset row must have a timestamp")

    folds_meta = build_walk_forward_folds(timestamps, config)
    results = []
    for fold in folds_meta:
        train_rows = [dataset[i] for i in fold.train_indices]
        test_rows = [dataset[i] for i in fold.test_indices]
        if not train_rows or not test_rows:
            continue
        model = fit_model(train_rows)
        predictions = predict(model, test_rows)
        metrics = score(predictions, test_rows)
        results.append(
            {
                "window": {
                    "train_start": fold.train_start.isoformat(),
                    "train_end": fold.train_end.isoformat(),
                    "test_start": fold.test_start.isoformat(),
                    "test_end": fold.test_end.isoformat(),
                },
                "metrics": metrics,
                "train_size": len(train_rows),
                "test_size": len(test_rows),
            }
        )
    return {"folds": results, "config": config.__dict__}
