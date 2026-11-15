"""Sensibilidad local: elasticidades del estado final respecto a cada parámetro."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, replace
from typing import Any

import numpy as np

from cliodinamica.core import simulate


def elasticities(
    model: Any,
    params: Any,
    y0: Sequence[float] | None = None,
    rel_step: float = 0.02,
    t_end: float = 500.0,
    n_points: int = 201,
) -> dict[str, dict[str, float]]:
    """Elasticidad e = (d f / f) / (d p / p) del estado final f ante cambios relativos de p.

    Se estima con diferencias centrales: p -> p (1 ± rel_step).
    """

    def final_state(p: Any) -> np.ndarray:
        return simulate(model, p, y0=y0, t_end=t_end, n_points=n_points).y[:, -1]

    base = final_state(params)
    safe = np.where(np.abs(base) > 1e-12, base, np.nan)
    out: dict[str, dict[str, float]] = {}
    for name, value in asdict(params).items():
        if value == 0:
            continue
        up = final_state(replace(params, **{name: value * (1 + rel_step)}))
        dn = final_state(replace(params, **{name: value * (1 - rel_step)}))
        e = (up - dn) / (2.0 * rel_step * safe)
        out[name] = dict(zip(model.state_names, map(float, e), strict=True))
    return out
