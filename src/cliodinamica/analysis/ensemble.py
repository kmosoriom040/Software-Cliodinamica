"""Ensamble Monte Carlo: propaga la incertidumbre de los parámetros."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np

from cliodinamica.core import simulate
from cliodinamica.ml.labeling import CLASSES, LabelRules, label_trajectory


@dataclass(frozen=True)
class Ensemble:
    t: np.ndarray
    y: np.ndarray  # (n_corridas, n_estados, n_tiempos)
    state_names: tuple[str, ...]
    labels: list[str]

    def percentiles(self, state: str, q: Sequence[float] = (5, 25, 50, 75, 95)) -> np.ndarray:
        """Percentiles de `state` en cada instante: forma (len(q), n_tiempos)."""
        return np.percentile(self.y[:, self.state_names.index(state), :], q, axis=0)

    def class_probabilities(self) -> dict[str, float]:
        total = max(len(self.labels), 1)
        return {c: self.labels.count(c) / total for c in CLASSES}


def run_ensemble(
    model: Any,
    params: Any,
    y0: Sequence[float] | None = None,
    n_runs: int = 200,
    rel_sigma: float = 0.1,
    t_end: float = 300.0,
    n_points: int = 301,
    seed: int = 0,
    perturb: Sequence[str] | None = None,
    rules: LabelRules | None = None,
) -> Ensemble:
    """Perturba cada parámetro con ruido lognormal de desviación `rel_sigma` y simula."""
    rng = np.random.default_rng(seed)
    base = asdict(params)
    names = list(base) if perturb is None else list(perturb)
    unknown = set(names) - set(base)
    if unknown:
        raise ValueError(f"Parámetros desconocidos: {sorted(unknown)}")
    runs, labels = [], []
    t = np.empty(0)
    for _ in range(n_runs):
        over = {k: base[k] * float(np.exp(rng.normal(0.0, rel_sigma))) for k in names}
        try:
            tray = simulate(model, replace(params, **over), y0=y0, t_end=t_end, n_points=n_points)
        except RuntimeError:
            continue
        runs.append(tray.y)
        labels.append(label_trajectory(tray, rules or LabelRules()))
        t = tray.t
    if not runs:
        raise RuntimeError("Ninguna simulación del ensamble terminó correctamente")
    return Ensemble(t=t, y=np.array(runs), state_names=tuple(model.state_names), labels=labels)
