"""
GFPS ML evaluation script

Loads trained models from backend/ml_models and evaluates them
on a fresh train/test split (or on a date-based split).
"""

import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    log_loss,
    classification_report
)
from joblib import load

from backend.db import SessionLocal
from backend.models import HistoricalMatch  # adjust if needed

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "backend" / "ml_models"


def fetch_historical_matches() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(HistoricalMatch).all()
    finally:
        db.close()

    if not rows:
        raise RuntimeError("No HistoricalMatch data found.")

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

    df["result_1x2"] = np.where(
        df["goals_home"] > df["goals_away"],
        0,
        np.where(df["goals_home"] == df["goals_away"], 1, 2),
    )
    df["total_goals"] = df["goals_home"] + df["goals_away"]
    df["is_over25"] = (df["total_goals"] > 2.5).astype(int)
    df["is_gg"] = ((df["goals_home"] >= 1) & (df["goals_away"] >= 1)).astype(int)

    return df


def build_feature_matrix(df: pd.DataFrame, model_feature_cols=None) -> pd.DataFrame:
    for col in ["odds_1", "odds_x", "odds_2", "odds_over25", "odds_under25", "odds_gg", "odds_ng"]:
        df[f"imp_{col}"] = 1.0 / df[col].replace(0, np.nan)

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

    if model_feature_cols is not None:
        # align columns with what model expects
        for c in model_feature_cols:
            if c not in X.columns:
                X[c] = 0.0
        X = X[model_feature_cols]

    return X


def eval_1x2(df: pd.DataFrame):
    path = MODELS_DIR / "model_1x2.joblib"
    if not path.exists():
        print("[GFPS-ML][EVAL-1X2] Model file not found:", path)
        return

    bundle = load(path)
    model = bundle["model"]
    feature_cols = bundle["feature_columns"]

    X = build_feature_matrix(df, model_feature_cols=feature_cols)
    y = df["result_1x2"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    probs = model.predict_proba(X_test)
    preds = probs.argmax(axis=1)

    acc = accuracy_score(y_test, preds)
    brier = np.mean(
        [
            brier_score_loss((y_test == k).astype(int), probs[:, k])
            for k in range(probs.shape[1])
        ]
    )
    ll = log_loss(y_test, probs)

    print("\n[GFPS-ML][EVAL-1X2]")
    print(f"Accuracy: {acc:.3f}")
    print(f"Brier:    {brier:.3f}")
    print(f"LogLoss:  {ll:.3f}")
    print("Class report:")
    print(classification_report(y_test, preds, digits=3))


def eval_over25(df: pd.DataFrame):
    path = MODELS_DIR / "model_over25.joblib"
    if not path.exists():
        print("[GFPS-ML][EVAL-O/U] Model file not found:", path)
        return

    bundle = load(path)
    model = bundle["model"]
    feature_cols = bundle["feature_columns"]

    X = build_feature_matrix(df, model_feature_cols=feature_cols)
    y = df["is_over25"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    brier = brier_score_loss(y_test, probs)
    ll = log_loss(y_test, np.vstack([1 - probs, probs]).T)

    print("\n[GFPS-ML][EVAL-O/U]")
    print(f"Accuracy: {acc:.3f}")
    print(f"Brier:    {brier:.3f}")
    print(f"LogLoss:  {ll:.3f}")


def eval_gg(df: pd.DataFrame):
    path = MODELS_DIR / "model_gg.joblib"
    if not path.exists():
        print("[GFPS-ML][EVAL-GG] Model file not found:", path)
        return

    bundle = load(path)
    model = bundle["model"]
    feature_cols = bundle["feature_columns"]

    X = build_feature_matrix(df, model_feature_cols=feature_cols)
    y = df["is_gg"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    brier = brier_score_loss(y_test, probs)
    ll = log_loss(y_test, np.vstack([1 - probs, probs]).T)

    print("\n[GFPS-ML][EVAL-GG]")
    print(f"Accuracy: {acc:.3f}")
    print(f"Brier:    {brier:.3f}")
    print(f"LogLoss:  {ll:.3f}")


def main():
    print("[GFPS-ML][EVAL] Loading historical matches...")
    df = fetch_historical_matches()
    print(f"[GFPS-ML][EVAL] Using {len(df)} matches.")

    eval_1x2(df)
    eval_over25(df)
    eval_gg(df)

    print("\n[GFPS-ML][EVAL] Done.")


if __name__ == "__main__":
    main()
