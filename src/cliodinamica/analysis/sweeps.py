"""Barridos de parámetros: diagrama 1D (tipo bifurcación) y mapa de regímenes 2D."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np

from cliodinamica.core import simulate
from cliodinamica.ml.labeling import CLASSES, LabelRules, extract_features, label_from_features


def _check_param(params: Any, name: str) -> None:
    if name not in asdict(params):
        raise ValueError(f"Parámetro desconocido: {name!r}")


@dataclass(frozen=True)
class Sweep:
    param: str
    values: np.ndarray
    state_names: tuple[str, ...]
    final: np.ndarray  # (n_valores, n_estados)
    tail_min: np.ndarray  # mínimo en la ventana final
    tail_max: np.ndarray  # máximo en la ventana final
    labels: list[str]


def sweep_1d(
    model: Any,
    base_params: Any,
    param: str,
    values: Sequence[float] | np.ndarray,
    y0: Sequence[float] | None = None,
    t_end: float = 500.0,
    n_points: int = 251,
    tail: float = 0.2,
    rules: LabelRules | None = None,
) -> Sweep:
    """Simula para cada valor de `param` y resume la ventana final de la trayectoria."""
    _check_param(base_params, param)
    rules = rules or LabelRules()
    vals = np.asarray(values, dtype=float)
    k = max(2, int(tail * n_points))
    final, lo, hi, labels = [], [], [], []
    for v in vals:
        tray = simulate(model, replace(base_params, **{param: float(v)}), y0=y0,
                        t_end=t_end, n_points=n_points)
        window = tray.y[:, -k:]
        final.append(tray.y[:, -1])
        lo.append(window.min(axis=1))
        hi.append(window.max(axis=1))
        labels.append(label_from_features(extract_features(tray), rules))
    return Sweep(param, vals, tuple(model.state_names), np.array(final), np.array(lo),
                 np.array(hi), labels)


@dataclass(frozen=True)
class RegimeMap:
    x_param: str
    y_param: str
    x_values: np.ndarray
    y_values: np.ndarray
    labels: np.ndarray  # (ny, nx): índice en CLASSES (NaN si la integración falló)
    n_final: np.ndarray
    s_final: np.ndarray

    def class_fractions(self) -> dict[str, float]:
        valid = self.labels[~np.isnan(self.labels)]
        total = max(len(valid), 1)
        return {c: float(np.sum(valid == i)) / total for i, c in enumerate(CLASSES)}


def regime_map(
    model: Any,
    base_params: Any,
    x_param: str,
    x_values: Sequence[float] | np.ndarray,
    y_param: str,
    y_values: Sequence[float] | np.ndarray,
    y0: Sequence[float] | None = None,
    t_end: float = 400.0,
    n_points: int = 201,
    rules: LabelRules | None = None,
) -> RegimeMap:
    """Clasifica el régimen final en una malla de dos parámetros."""
    _check_param(base_params, x_param)
    _check_param(base_params, y_param)
    if x_param == y_param:
        raise ValueError("Los dos parámetros del mapa deben ser distintos")
    rules = rules or LabelRules()
    xs = np.asarray(x_values, dtype=float)
    ys = np.asarray(y_values, dtype=float)
    labels = np.full((len(ys), len(xs)), np.nan)
    n_final = np.full_like(labels, np.nan)
    s_final = np.full_like(labels, np.nan)
    s_idx = list(model.state_names).index("S") if "S" in model.state_names else None
    for iy, yv in enumerate(ys):
        for ix, xv in enumerate(xs):
            p = replace(base_params, **{x_param: float(xv), y_param: float(yv)})
            try:
                tray = simulate(model, p, y0=y0, t_end=t_end, n_points=n_points)
            except RuntimeError:
                continue
            feats = extract_features(tray)
            labels[iy, ix] = CLASSES.index(label_from_features(feats, rules))
            n_final[iy, ix] = tray.y[0, -1]
            if s_idx is not None:
                s_final[iy, ix] = tray.y[s_idx, -1]
    return RegimeMap(x_param, y_param, xs, ys, labels, n_final, s_final)
