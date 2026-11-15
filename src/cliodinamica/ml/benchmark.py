"""Validación del clasificador: validación cruzada frente a modelos base e importancias."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .classifier import StateClassifier


def compare_models(
    df: pd.DataFrame, columns: Sequence[str], cv: int = 5, seed: int = 0
) -> dict[str, tuple[float, float]]:
    """Exactitud (media, desviación) en validación cruzada estratificada."""
    X, y = df[list(columns)], df["label"]
    models = {
        "MLP": StateClassifier(random_state=seed).pipeline,
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=seed),
        "Regresión logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    }
    folds = StratifiedKFold(cv, shuffle=True, random_state=seed)
    out = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=folds)
        out[name] = (float(scores.mean()), float(scores.std()))
    return out


def permutation_importances(
    df: pd.DataFrame,
    columns: Sequence[str],
    test_size: float = 0.25,
    seed: int = 0,
    n_repeats: int = 10,
) -> dict[str, tuple[float, float]]:
    """Caída de exactitud al permutar cada columna (conjunto de prueba), de mayor a menor."""
    X, y = df[list(columns)], df["label"]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    clf = StateClassifier(random_state=seed).fit(X_tr, y_tr)
    res = permutation_importance(clf.pipeline, X_te, y_te, n_repeats=n_repeats,
                                 random_state=seed)
    pairs = zip(columns, res.importances_mean, res.importances_std, strict=True)
    ranked = sorted(pairs, key=lambda c: c[1], reverse=True)
    return {name: (float(m), float(s)) for name, m, s in ranked}
