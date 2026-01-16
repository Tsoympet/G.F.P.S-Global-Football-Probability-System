from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Iterable, TypeVar

from ..data_providers.base import FixtureRecord, ResultRecord
from ..data_normalization import normalize_timezone

T = TypeVar("T")
MINUTES_PER_DAY = 1440
SCORE_OUTLIER_THRESHOLD = 20


def validate_fixture_schema(record: FixtureRecord) -> FixtureRecord:
    # Pydantic validation already applies on creation; ensure timezone normalization.
    record.kickoff = normalize_timezone(record.kickoff)
    return record


def validate_result_schema(record: ResultRecord) -> ResultRecord:
    record.kickoff = normalize_timezone(record.kickoff)
    if record.home_score < 0 or record.away_score < 0:
        raise ValueError("Negative scores are not allowed")
    return record


def detect_anomalies(record: ResultRecord) -> list[str]:
    issues: list[str] = []
    if record.home_score > SCORE_OUTLIER_THRESHOLD or record.away_score > SCORE_OUTLIER_THRESHOLD:
        issues.append("score_out_of_bounds")
    if record.kickoff > datetime.now(timezone.utc):
        issues.append("kickoff_in_future_for_result")
    return issues


def confidence_score(
    record: FixtureRecord | ResultRecord,
    source_priority: int = 1,
    freshness_minutes: int = 0,
) -> float:
    recency = max(0, MINUTES_PER_DAY - freshness_minutes) / MINUTES_PER_DAY  # 0..1
    return source_priority + recency


def deduplicate_records(
    records: Iterable[T],
    key_func: Callable[[T], str],
    confidence_func: Callable[[T], float],
) -> list[T]:
    best: dict[str, tuple[T, float]] = {}
    for rec in records:
        key = key_func(rec)
        score = confidence_func(rec)
        stored = best.get(key)
        if stored is None or score > stored[1]:
            best[key] = (rec, score)
    return [pair[0] for pair in best.values()]
