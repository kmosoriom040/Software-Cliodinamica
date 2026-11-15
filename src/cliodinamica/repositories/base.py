"""Interfaz común de los repositorios."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from cliodinamica.services.simulation import SimulationResult


class Repository(Protocol):
    def save(self, result: SimulationResult) -> str:
        """Guarda el resultado y devuelve su ubicación (ruta o identificador)."""
        ...
