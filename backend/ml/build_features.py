"""Feature builder utilities."""
from __future__ import annotations

from typing import Iterable, List, Tuple
import numpy as np
import pandas as pd

from .feature_schema import MatchFeatures


def build_feature_matrix(records: Iterable[MatchFeatures]) -> Tuple[pd.DataFrame, List[str]]:
    rows = []
    ids = []
    for rec in records:
        ids.append(rec.fixture_id)
        rows.append(rec.to_vector())
    frame = pd.DataFrame(rows)
    frame.fillna(0.0, inplace=True)
    columns = list(frame.columns)
    return frame, ids


def build_label_vector(results: Iterable[str]) -> np.ndarray:
    mapping = {"home": 0, "draw": 1, "away": 2}
    return np.array([mapping[r] for r in results], dtype=int)


