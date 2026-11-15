"""Registro de modelos (patrón Factory): crea modelos a partir de su nombre."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_REGISTRY: dict[str, type] = {}


def register(name: str) -> Callable[[type], type]:
    """Decorador que añade una clase de modelo al registro bajo `name`."""

    def decorator(cls: type) -> type:
        _REGISTRY[name] = cls
        return cls

    return decorator


def available_models() -> list[str]:
    return sorted(_REGISTRY)


def create_model(name: str) -> Any:
    try:
        cls = _REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"Modelo desconocido: {name!r}. Disponibles: {available_models()}"
        ) from None
    return cls()
