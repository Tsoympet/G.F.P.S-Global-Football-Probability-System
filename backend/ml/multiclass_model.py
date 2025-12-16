"""Baseline multiclass classifiers for 1X2 prediction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss


@dataclass
class ModelBundle:
    model: object
    label_mapping: dict

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probs = self.model.predict_proba(X)
        probs = probs / probs.sum(axis=1, keepdims=True)
        return probs


def train_logistic(X: np.ndarray, y: np.ndarray, C: float = 1.0) -> ModelBundle:
    clf = LogisticRegression(max_iter=500, multi_class="multinomial", C=C)
    clf.fit(X, y)
    return ModelBundle(model=clf, label_mapping={0: "home", 1: "draw", 2: "away"})


def train_gradient_boosting(X: np.ndarray, y: np.ndarray, n_estimators: int = 200) -> ModelBundle:
    clf = GradientBoostingClassifier(n_estimators=n_estimators)
    clf.fit(X, y)
    return ModelBundle(model=clf, label_mapping={0: "home", 1: "draw", 2: "away"})


def validate_model(bundle: ModelBundle, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> float:
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
    model = bundle.model
    model.fit(X_train, y_train)
    probs = model.predict_proba(X_val)
    return float(log_loss(y_val, probs))


