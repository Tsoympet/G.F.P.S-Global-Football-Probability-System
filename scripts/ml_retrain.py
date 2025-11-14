"""
GFPS ML retraining script

Trains ML models for:
  - 1X2 full-time result (multi-class)
  - Over/Under 2.5 (binary)
  - GG / NG (Both Teams To Score) (binary)

Requirements (add to backend/requirements.txt):
  numpy
  pandas
  scikit-learn
  joblib

This script assumes you have a HistoricalMatch model in backend.models with fields:
  - id
  - league (str)
  - league_id (int)
  - home (str)
  - away (str)
  - goals_home (int)
  - goals_away (int)
  - odds_1 (float)
  - odds_x (float)
  - odds_2 (float)
  - odds_over25 (float)
  - odds_under25 (float)
  - odds_gg (float)
  - odds_ng (float)
  - kickoff (datetime or date)
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    log_loss,
    classification_report
)
from joblib import dump

from backend.db import SessionLocal
from backend.models import HistoricalMatch  # adjust import if needed

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "backend" / "ml_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_historical_matches(min_matches: int = 2000) -> pd.DataFrame:
    """
    Load historical matches from DB into a pandas DataFrame.
    """
    db = SessionLocal()
    try:
        q = db.query(HistoricalMatch)
        rows = q.all()
    finally:
        db.close()

    if not rows:
        raise RuntimeError("No HistoricalMatch data found in DB.")

    data = []
    for m in rows:
        data.append(
            {
                "league": m.league,
                "league_id": m.league_id,
                "home": m.home,
                "away": m.away,
                "goals_home": m.goals_home,
                "goals_away": m.goals_away,
                "odds_1": m.odds_1,
                "odds_x": m.odds_x,
                "odds_2": m.odds_2,
                "odds_over25": m.odds_over25,
                "odds_under25": m.odds_under25,
                "odds_gg": m.odds_gg,
                "odds_ng": m.odds_ng,
                "kickoff": m.kickoff,
            }
        )

    df = pd.DataFrame(data)
    print(f"[GFPS-ML] Loaded {len(df)} matches.")

    if len(df) < min_matches:
        print(
            f"[GFPS-ML] WARNING: Only {len(df)} matches, "
            f"recommended minimum is {min_matches}."
        )

    # basic cleaning: drop rows with missing key odds or goals
    df = df.dropna(
        subset=[
            "goals_home",
            "goals_away",
            "odds_1",
            "odds_x",
            "odds_2",
            "odds_over25",
            "odds_under25",
            "odds_gg",
            "odds_ng",
        ]
    )

    # compute result labels
    df["result_1x2"] = np.where(
        df["goals_home"] > df["goals_away"],
        0,
        np.where(df["goals_home"] == df["goals_away"], 1, 2),
    )  # 0=1,1=X,2=2

    df["total_goals"] = df["goals_home"] + df["goals_away"]
    df["is_over25"] = (df["total_goals"] > 2.5).astype(int)
    df["is_gg"] = ((df["goals_home"] >= 1) & (df["goals_away"] >= 1)).astype(int)

    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build generic feature matrix from historical data.
    Here we use:
      - implied probabilities from odds
      - league dummy encoding (optional simple)
    """
    # implied probabilities from closing odds
    for col in ["odds_1", "odds_x", "odds_2", "odds_over25", "odds_under25", "odds_gg", "odds_ng"]:
        df[f"imp_{col}"] = 1.0 / df[col].replace(0, np.nan)

    # simple league encoding: top N leagues as dummies, rest as "other"
    top_leagues = df["league"].value_counts().head(10).index.tolist()
    df["league_bucket"] = df["league"].where(df["league"].isin(top_leagues), "Other")

    league_dummies = pd.get_dummies(df["league_bucket"], prefix="lg")

    feature_cols = [
        "imp_odds_1",
        "imp_odds_x",
        "imp_odds_2",
        "imp_odds_over25",
        "imp_odds_under25",
        "imp_odds_gg",
        "imp_odds_ng",
    ]

    X = pd.concat([df[feature_cols], league_dummies], axis=1)
    return X


def train_1x2_model(df: pd.DataFrame):
    print("[GFPS-ML] Training 1X2 model...")
    X = build_feature_matrix(df)
    y = df["result_1x2"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = LogisticRegression(
        multi_class="multinomial", max_iter=200, n_jobs=-1
    )
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)
    preds = probs.argmax(axis=1)

    acc = accuracy_score(y_test, preds)
    # multi-class Brier: average over classes
    brier = np.mean(
        [
            brier_score_loss((y_test == k).astype(int), probs[:, k])
            for k in range(probs.shape[1])
        ]
    )
    ll = log_loss(y_test, probs)

    print(f"[GFPS-ML][1X2] Accuracy: {acc:.3f}")
    print(f"[GFPS-ML][1X2] Brier:    {brier:.3f}")
    print(f"[GFPS-ML][1X2] LogLoss:  {ll:.3f}")
    print("[GFPS-ML][1X2] Class report:")
    print(classification_report(y_test, preds, digits=3))

    path = MODELS_DIR / "model_1x2.joblib"
    dump(
        {
            "model": model,
            "feature_columns": X.columns.tolist(),
        },
        path,
    )
    print(f"[GFPS-ML][1X2] Saved model to {path}")


def train_over25_model(df: pd.DataFrame):
    print("[GFPS-ML] Training Over/Under 2.5 model...")
    X = build_feature_matrix(df)
    y = df["is_over25"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=200, n_jobs=-1)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    brier = brier_score_loss(y_test, probs)
    ll = log_loss(y_test, np.vstack([1 - probs, probs]).T)

    print(f"[GFPS-ML][O/U] Accuracy: {acc:.3f}")
    print(f"[GFPS-ML][O/U] Brier:    {brier:.3f}")
    print(f"[GFPS-ML][O/U] LogLoss:  {ll:.3f}")

    path = MODELS_DIR / "model_over25.joblib"
    dump(
        {
            "model": model,
            "feature_columns": X.columns.tolist(),
        },
        path,
    )
    print(f"[GFPS-ML][O/U] Saved model to {path}")


def train_gg_model(df: pd.DataFrame):
    print("[GFPS-ML] Training GG/NG model...")
    X = build_feature_matrix(df)
    y = df["is_gg"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=200, n_jobs=-1)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    brier = brier_score_loss(y_test, probs)
    ll = log_loss(y_test, np.vstack([1 - probs, probs]).T)

    print(f"[GFPS-ML][GG] Accuracy: {acc:.3f}")
    print(f"[GFPS-ML][GG] Brier:    {brier:.3f}")
    print(f"[GFPS-ML][GG] LogLoss:  {ll:.3f}")

    path = MODELS_DIR / "model_gg.joblib"
    dump(
        {
            "model": model,
            "feature_columns": X.columns.tolist(),
        },
        path,
    )
    print(f"[GFPS-ML][GG] Saved model to {path}")


def main():
    print("[GFPS-ML] Starting ML retraining...")
    df = fetch_historical_matches()
    print(f"[GFPS-ML] Using {len(df)} cleaned matches for training.")

    train_1x2_model(df)
    train_over25_model(df)
    train_gg_model(df)

    print("[GFPS-ML] All models trained and saved.")


if __name__ == "__main__":
    main()
