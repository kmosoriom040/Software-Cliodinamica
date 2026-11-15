"""Núcleo científico: modelos ODE, registro de modelos y solver."""

from . import models  # noqa: F401  (registra los modelos disponibles)
from .registry import available_models, create_model, register
from .solver import Trajectory, simulate

__all__ = ["Trajectory", "available_models", "create_model", "register", "simulate"]
