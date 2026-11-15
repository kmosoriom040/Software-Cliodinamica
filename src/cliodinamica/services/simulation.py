"""SimulationService: punto de entrada único para la interfaz y la API."""

from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

from cliodinamica.core import Trajectory, create_model, simulate
from cliodinamica.repositories.base import Repository


@dataclass(frozen=True)
class SimulationResult:
    run_id: str
    model: str
    params: dict[str, float]
    t_end: float
    created_at: str
    trajectory: Trajectory


class SimulationService:
    def __init__(self, repository: Repository | None = None) -> None:
        self._repository = repository

    def run(
        self,
        model: str = "cliodinamica",
        params: Mapping[str, float] | None = None,
        y0: Sequence[float] | None = None,
        t_end: float = 300.0,
        n_points: int = 601,
        save: bool = False,
    ) -> SimulationResult:
        ode = create_model(model)
        p = self._build_params(ode, params)
        trajectory = simulate(ode, p, y0=y0, t_end=t_end, n_points=n_points)
        result = SimulationResult(
            run_id=uuid.uuid4().hex[:12],
            model=ode.name,
            params=asdict(p),
            t_end=t_end,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            trajectory=trajectory,
        )
        if save:
            self.save(result)
        return result

    def save(self, result: SimulationResult) -> str:
        if self._repository is None:
            raise RuntimeError("El servicio no tiene un repositorio configurado")
        return self._repository.save(result)

    @staticmethod
    def _build_params(model: Any, overrides: Mapping[str, float] | None) -> Any:
        base = model.default_params()
        if not overrides:
            return base
        unknown = set(overrides) - set(asdict(base))
        if unknown:
            raise ValueError(f"Parámetros desconocidos: {sorted(unknown)}")
        return replace(base, **overrides)
