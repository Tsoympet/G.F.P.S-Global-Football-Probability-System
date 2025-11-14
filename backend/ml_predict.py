"""
backend/ml_predict.py

Helper για χρήση των ML μοντέλων του GFPS από το backend.

Χρησιμοποιεί τα joblib αρχεία από backend/ml_models:
  - model_1x2.joblib
  - model_over25.joblib
  - model_gg.joblib

Παρέχει συναρτήσεις:
  - predict_1x2_proba(...)
  - predict_over25_proba(...)
  - predict_gg_proba(...)

Κοινή λογική features με τα scripts ml_retrain/ml_eval.
"""

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from joblib import load

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "ml_models"

_model_cache: Dict[str, Dict] = {}


def _load_model(name: str) -> Dict:
    """
    Lazy-load model bundle από joblib.
    Επιστρέφει:
      {"model": sklearn_model, "feature_columns": [..]}
    """
    if name in _model_cache:
        return _model_cache[name]

    path = MODELS_DIR / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(f"ML model file not found: {path}")

    bundle = load(path)
    _model_cache[name] = bundle
    return bundle


def _build_feature_row(
    league: str,
    odds_1: float,
    odds_x: float,
    odds_2: float,
    odds_over25: float,
    odds_under25: float,
    odds_gg: float,
    odds_ng: float,
    feature_columns: list,
) -> pd.DataFrame:
    """
    Κατασκευάζει ένα single-row DataFrame με τα features που περιμένει το μοντέλο.
    Χρησιμοποιεί implied probabilities + one-hot league bucket.
    """
    data = {
        "odds_1": odds_1,
        "odds_x": odds_x,
        "odds_2": odds_2,
        "odds_over25": odds_over25,
        "odds_under25": odds_under25,
        "odds_gg": odds_gg,
        "odds_ng": odds_ng,
        "league": league or "Unknown",
    }
    df = pd.DataFrame([data])

    # Implied probabilities (απλή μεταφορά από retrain logic)
    for col in [
        "odds_1",
        "odds_x",
        "odds_2",
        "odds_over25",
        "odds_under25",
        "odds_gg",
        "odds_ng",
    ]:
        df[f"imp_{col}"] = 1.0 / df[col].replace(0, np.nan)

    # League bucket – εδώ απλό: αυτή η λίγκα είναι το δικό της bucket
    # και όλα τα άλλα θα γίνουν zero όταν align-άρουμε τα columns.
    df["league_bucket"] = df["league"]
    league_dummies = pd.get_dummies(df["league_bucket"], prefix="lg")

    feature_cols_base = [
        "imp_odds_1",
        "imp_odds_x",
        "imp_odds_2",
        "imp_odds_over25",
        "imp_odds_under25",
        "imp_odds_gg",
        "imp_odds_ng",
    ]
    X = pd.concat([df[feature_cols_base], league_dummies], axis=1)

    # align columns με αυτά που έχει το μοντέλο
    for col in feature_columns:
        if col not in X.columns:
            X[col] = 0.0
    X = X[feature_columns]

    return X


def predict_1x2_proba(
    league: str,
    odds_1: float,
    odds_x: float,
    odds_2: float,
    odds_over25: float,
    odds_under25: float,
    odds_gg: float,
    odds_ng: float,
) -> Tuple[float, float, float]:
    """
    Επιστρέφει probabilities (p1, px, p2) με βάση το ML 1X2 model.
    """
    bundle = _load_model("model_1x2")
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    X = _build_feature_row(
        league,
        odds_1,
        odds_x,
        odds_2,
        odds_over25,
        odds_under25,
        odds_gg,
        odds_ng,
        feature_columns,
    )
    probs = model.predict_proba(X)[0]
    # order: class 0=1, 1=X, 2=2
    return float(probs[0]), float(probs[1]), float(probs[2])


def predict_over25_proba(
    league: str,
    odds_1: float,
    odds_x: float,
    odds_2: float,
    odds_over25: float,
    odds_under25: float,
    odds_gg: float,
    odds_ng: float,
) -> float:
    """
    Επιστρέφει probability P(Over 2.5 goals).
    """
    bundle = _load_model("model_over25")
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    X = _build_feature_row(
        league,
        odds_1,
        odds_x,
        odds_2,
        odds_over25,
        odds_under25,
        odds_gg,
        odds_ng,
        feature_columns,
    )
    probs = model.predict_proba(X)[0]
    # binary: probs[1] = P(Over)
    return float(probs[1])


def predict_gg_proba(
    league: str,
    odds_1: float,
    odds_x: float,
    odds_2: float,
    odds_over25: float,
    odds_under25: float,
    odds_gg: float,
    odds_ng: float,
) -> float:
    """
    Επιστρέφει probability P(GG - Both Teams To Score).
    """
    bundle = _load_model("model_gg")
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    X = _build_feature_row(
        league,
        odds_1,
        odds_x,
        odds_2,
        odds_over25,
        odds_under25,
        odds_gg,
        odds_ng,
        feature_columns,
    )
    probs = model.predict_proba(X)[0]
    # binary: probs[1] = P(GG)
    return float(probs[1])
