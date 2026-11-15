"""Generación del dataset: muestreo Latin Hypercube de parámetros y estado inicial."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
from scipy.stats import qmc

from cliodinamica.core import create_model, simulate

from .labeling import LabelRules, extract_features, label_from_features

PARAM_BOUNDS = {
    "r": (0.005, 0.10),
    "kappa": (0.5, 3.0),
    "rho": (0.01, 0.10),
    "gamma": (0.001, 0.05),
    "alpha": (0.01, 0.20),
    "delta": (0.01, 0.10),
    "sigma": (0.02, 0.30),
    "lam": (0.05, 1.0),
}
STATE_BOUNDS = {
    "y0_N": (0.1, 2.0),
    "y0_R": (0.3, 1.0),
    "y0_G": (0.0, 0.8),
    "y0_S": (0.3, 1.0),
}
INPUT_COLUMNS = (*PARAM_BOUNDS, *STATE_BOUNDS)


def generate_dataset(
    n_samples: int = 2000,
    seed: int = 0,
    t_end: float = 500.0,
    n_points: int = 251,
    rules: LabelRules | None = None,
) -> pd.DataFrame:
    rules = rules or LabelRules()
    model = create_model("cliodinamica")
    base = model.default_params()
    bounds = {**PARAM_BOUNDS, **STATE_BOUNDS}
    names = list(bounds)
    lo = [bounds[k][0] for k in names]
    hi = [bounds[k][1] for k in names]
    sample = qmc.scale(qmc.LatinHypercube(d=len(names), seed=seed).random(n_samples), lo, hi)

    rows = []
    for vec in sample:
        values = dict(zip(names, map(float, vec), strict=True))
        params = replace(base, **{k: values[k] for k in PARAM_BOUNDS})
        y0 = [values[f"y0_{s}"] for s in model.state_names]
        try:
            tray = simulate(model, params, y0=y0, t_end=t_end, n_points=n_points)
        except RuntimeError:
            continue
        feats = extract_features(tray)
        rows.append({**values, **feats, "label": label_from_features(feats, rules)})
    return pd.DataFrame(rows)
