"""Rasgos de una trayectoria y reglas de etiquetado (crecimiento, estancamiento, colapso)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cliodinamica.core import Trajectory

CLASSES = ("crecimiento", "estancamiento", "colapso")

FEATURE_COLUMNS = ("delta", "n_max_ratio", "n_final_ratio", "s_min", "s_final", "g_final")


@dataclass(frozen=True)
class LabelRules:
    """Umbrales de ejemplo, ajustables."""

    growth: float = 0.10  # crecimiento relativo mínimo de N para llamarlo "crecimiento"
    collapse_s: float = 0.20  # estabilidad final por debajo de la cual hay colapso
    collapse_n: float = 0.50  # fracción del máximo de N por debajo de la cual hay colapso


def extract_features(tray: Trajectory) -> dict[str, float]:
    n, s, g = tray.series("N"), tray.series("S"), tray.series("G")
    n0 = max(float(n[0]), 1e-12)
    n_max = max(float(n.max()), 1e-12)
    return {
        "delta": float(n[-1]) / n0 - 1.0,  # (N(T) - N(0)) / N(0)
        "n_max_ratio": n_max / n0,
        "n_final_ratio": float(n[-1]) / n_max,
        "s_min": float(s.min()),
        "s_final": float(s[-1]),
        "g_final": float(g[-1]),
    }


def label_from_features(f: dict[str, float], rules: LabelRules = LabelRules()) -> str:
    """El colapso se evalúa primero; luego crecimiento; lo demás es estancamiento."""
    if f["n_final_ratio"] < rules.collapse_n or f["s_final"] < rules.collapse_s:
        return "colapso"
    if f["delta"] > rules.growth:
        return "crecimiento"
    return "estancamiento"


def label_trajectory(tray: Trajectory, rules: LabelRules = LabelRules()) -> str:
    return label_from_features(extract_features(tray), rules)


def feature_vector(tray: Trajectory) -> np.ndarray:
    f = extract_features(tray)
    return np.array([f[c] for c in FEATURE_COLUMNS])
