"""Clasificador MLP del estado del sistema (scikit-learn)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .labeling import CLASSES


class StateClassifier:
    def __init__(self, hidden_layer_sizes: tuple[int, ...] = (32, 16), random_state: int = 0):
        self.pipeline = make_pipeline(
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=hidden_layer_sizes,
                max_iter=1000,
                early_stopping=True,
                random_state=random_state,
            ),
        )

    def fit(self, X: Any, y: Any) -> StateClassifier:
        self.pipeline.fit(X, y)
        return self

    def predict(self, X: Any):
        return self.pipeline.predict(X)

    def predict_proba(self, X: Any):
        return self.pipeline.predict_proba(X)

    @property
    def classes_(self):
        return self.pipeline.classes_

    def save(self, path: str | Path) -> None:
        joblib.dump(self, path)

    @staticmethod
    def load(path: str | Path) -> StateClassifier:
        return joblib.load(path)


def evaluate(
    df: pd.DataFrame,
    columns: Sequence[str],
    test_size: float = 0.25,
    seed: int = 0,
    hidden_layer_sizes: tuple[int, ...] = (32, 16),
) -> tuple[StateClassifier, dict]:
    """Entrena con una partición estratificada y mide en la parte de prueba."""
    X, y = df[list(columns)], df["label"]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    clf = StateClassifier(hidden_layer_sizes, random_state=seed).fit(X_tr, y_tr)
    pred = clf.predict(X_te)
    labels = [c for c in CLASSES if c in set(y)]
    metrics = {
        "accuracy": float(accuracy_score(y_te, pred)),
        "labels": labels,
        "confusion_matrix": confusion_matrix(y_te, pred, labels=labels).tolist(),
        "report": classification_report(y_te, pred, labels=labels, output_dict=True,
                                        zero_division=0),
    }
    return clf, metrics
