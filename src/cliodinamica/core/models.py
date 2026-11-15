"""Modelos ODE. Cada modelo cumple el protocolo `OdeModel` (patrón Strategy)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from .registry import register

_EPS = 1e-9


class OdeModel(Protocol):
    name: str
    state_names: tuple[str, ...]

    def default_params(self) -> Any: ...

    def default_y0(self) -> np.ndarray: ...

    def rhs(self, t: float, y: np.ndarray, params: Any) -> np.ndarray: ...


@dataclass(frozen=True)
class ClioParams:
    """Parámetros del modelo estructural-demográfico (valores de ejemplo)."""

    r: float = 0.02  # crecimiento poblacional
    kappa: float = 1.5  # población sostenible por unidad de recurso
    rho: float = 0.04  # regeneración de recursos
    R0: float = 1.0  # capacidad de carga de recursos
    gamma: float = 0.01  # extracción por habitante
    alpha: float = 0.05  # generación de desigualdad por presión demográfica
    delta: float = 0.03  # redistribución o amortiguación
    sigma: float = 0.10  # recuperación de la estabilidad
    lam: float = 0.20  # erosión de la estabilidad (lambda)


@register("cliodinamica")
class Cliodinamica:
    """dN/dt, dR/dt, dG/dt, dS/dt con presión demográfica psi = N / (kappa * R)."""

    name = "cliodinamica"
    state_names = ("N", "R", "G", "S")

    def default_params(self) -> ClioParams:
        return ClioParams()

    def default_y0(self) -> np.ndarray:
        return np.array([0.3, 1.0, 0.1, 0.9])

    def rhs(self, t: float, y: np.ndarray, p: ClioParams) -> np.ndarray:
        n, res, g, s = y
        psi = n / (p.kappa * max(res, _EPS))
        dn = p.r * n * (1.0 - psi)
        dr = p.rho * res * (1.0 - res / p.R0) - p.gamma * n * res
        dg = p.alpha * psi * (1.0 - g) - p.delta * g
        ds = p.sigma * (1.0 - s) - p.lam * g * psi * s
        return np.array([dn, dr, dg, ds])

    def equilibrium(self, p: ClioParams) -> np.ndarray:
        """Equilibrio interior (psi = 1), obtenido de forma analítica."""
        res = p.rho / (p.rho / p.R0 + p.gamma * p.kappa)
        g = p.alpha / (p.alpha + p.delta)
        s = p.sigma / (p.sigma + p.lam * g)
        return np.array([p.kappa * res, res, g, s])


@dataclass(frozen=True)
class LVParams:
    a: float = 0.10  # crecimiento de la presa
    b: float = 0.02  # depredación
    c: float = 0.10  # mortalidad del depredador
    d: float = 0.01  # conversión de presa en depredador


@register("lotka_volterra")
class LotkaVolterra:
    """Modelo presa-depredador clásico, útil como segundo modelo de referencia."""

    name = "lotka_volterra"
    state_names = ("x", "y")

    def default_params(self) -> LVParams:
        return LVParams()

    def default_y0(self) -> np.ndarray:
        return np.array([15.0, 5.0])

    def rhs(self, t: float, y: np.ndarray, p: LVParams) -> np.ndarray:
        x, z = y
        return np.array([p.a * x - p.b * x * z, -p.c * z + p.d * x * z])
