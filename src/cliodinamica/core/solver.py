"""Solver: adapta `scipy.integrate.solve_ivp` a la interfaz del proyecto."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Trajectory:
    """Resultado de una simulación. `y` tiene forma (n_estados, n_tiempos)."""

    t: np.ndarray
    y: np.ndarray
    state_names: tuple[str, ...]

    def series(self, name: str) -> np.ndarray:
        return self.y[self.state_names.index(name)]

    def as_dict(self) -> dict[str, np.ndarray]:
        return {"t": self.t, **{n: self.series(n) for n in self.state_names}}


def simulate(
    model: Any,
    params: Any | None = None,
    y0: Sequence[float] | None = None,
    t_end: float = 300.0,
    n_points: int = 601,
    method: str = "LSODA",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    events: Callable | Sequence[Callable] | None = None,
) -> Trajectory:
    """Integra el modelo en [0, t_end] y devuelve la trayectoria."""
    params = model.default_params() if params is None else params
    y_init = model.default_y0() if y0 is None else np.asarray(y0, dtype=float)

    if y_init.shape != (len(model.state_names),):
        raise ValueError(
            f"y0 debe tener {len(model.state_names)} componentes, recibió {y_init.shape}"
        )
    if np.any(y_init < 0):
        raise ValueError("El estado inicial no puede tener componentes negativas")
    if t_end <= 0 or n_points < 2:
        raise ValueError("t_end debe ser positivo y n_points al menos 2")

    sol = solve_ivp(
        model.rhs,
        (0.0, t_end),
        y_init,
        args=(params,),
        method=method,
        t_eval=np.linspace(0.0, t_end, n_points),
        rtol=rtol,
        atol=atol,
        events=events,
    )
    if not sol.success:
        raise RuntimeError(f"La integración falló: {sol.message}")
    return Trajectory(t=sol.t, y=sol.y, state_names=tuple(model.state_names))
