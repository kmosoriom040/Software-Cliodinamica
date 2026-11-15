"""Equilibrios, Jacobiano numérico y criterio de autovalores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

_TOL = 1e-7


def jacobian(model: Any, y: np.ndarray, params: Any, eps: float = 1e-6) -> np.ndarray:
    """Jacobiano de rhs en `y` por diferencias centrales: J[i, j] = d f_i / d y_j."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    jac = np.zeros((n, n))
    for j in range(n):
        h = eps * max(1.0, abs(y[j]))
        yp, ym = y.copy(), y.copy()
        yp[j] += h
        ym[j] -= h
        jac[:, j] = (model.rhs(0.0, yp, params) - model.rhs(0.0, ym, params)) / (2.0 * h)
    return jac


@dataclass(frozen=True)
class EquilibriumReport:
    point: np.ndarray
    jacobian: np.ndarray
    eigenvalues: np.ndarray
    kind: str

    @property
    def stable(self) -> bool:
        return bool(np.all(self.eigenvalues.real < -_TOL))


def analyze_equilibrium(
    model: Any, params: Any, point: np.ndarray | None = None
) -> EquilibriumReport:
    """Clasifica el equilibrio (por defecto el que entrega `model.equilibrium`)."""
    pt = np.asarray(model.equilibrium(params) if point is None else point, dtype=float)
    jac = jacobian(model, pt, params)
    eig = np.linalg.eigvals(jac)
    if np.all(eig.real < -_TOL):
        kind = "estable (foco)" if np.any(np.abs(eig.imag) > _TOL) else "estable (nodo)"
    elif np.any(eig.real > _TOL):
        kind = "inestable"
    else:
        kind = "marginal (centro o no hiperbólico)"
    return EquilibriumReport(point=pt, jacobian=jac, eigenvalues=eig, kind=kind)
