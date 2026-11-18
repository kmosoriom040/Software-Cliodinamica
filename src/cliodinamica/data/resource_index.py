"""Construcción y análisis de sensibilidad de índices compuestos de recursos.

Este módulo no descarga datos ni infiere límites de normalización. Los límites
de referencia deben proceder de una decisión metodológica documentada.
Los valores faltantes se conservan y no se imputan: un índice anual solo se
calcula cuando todos sus componentes están disponibles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class ResourceIndexResult:
    """Índices agregados y componentes normalizados por año."""

    years: NDArray[np.int64]
    component_names: tuple[str, ...]
    components: FloatArray  # shape: (n_years, n_components)
    weights: FloatArray  # shape: (n_components,)
    arithmetic: FloatArray  # shape: (n_years,)
    geometric: FloatArray  # shape: (n_years,)
    complete: NDArray[np.bool_]


@dataclass(frozen=True)
class WeightSensitivityResult:
    """Distribuciones de índices generadas por pesos muestreados."""

    component_names: tuple[str, ...]
    weight_samples: FloatArray  # shape: (n_samples, n_components)
    arithmetic_samples: FloatArray  # shape: (n_samples, n_years)
    geometric_samples: FloatArray  # shape: (n_samples, n_years)
    arithmetic_quantiles: FloatArray  # shape: (3, n_years): p05, p50, p95
    geometric_quantiles: FloatArray  # shape: (3, n_years): p05, p50, p95


def normalize_indicator(
    values: Sequence[float] | NDArray[np.floating],
    *,
    lower_bound: float,
    upper_bound: float,
    higher_is_better: bool = True,
    clip: bool = True,
) -> FloatArray:
    """Normaliza un indicador con límites externos fijos a [0, 1].

    NaN se conserva como dato faltante. No se calculan límites a partir de la
    muestra, para evitar que el índice cambie retrospectivamente al añadir años.
    """
    if not np.isfinite(lower_bound) or not np.isfinite(upper_bound):
        raise ValueError("Los límites de referencia deben ser finitos.")
    if upper_bound <= lower_bound:
        raise ValueError("upper_bound debe ser mayor que lower_bound.")

    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError("El indicador debe ser una secuencia unidimensional.")

    normalized = (array - lower_bound) / (upper_bound - lower_bound)
    if not higher_is_better:
        normalized = 1.0 - normalized
    if clip:
        normalized = np.clip(normalized, 0.0, 1.0)
    return normalized.astype(float, copy=False)


def _validate_components(
    years: Sequence[int] | NDArray[np.integer],
    components: Mapping[str, Sequence[float] | NDArray[np.floating]],
) -> tuple[NDArray[np.int64], tuple[str, ...], FloatArray]:
    year_array = np.asarray(years, dtype=np.int64)
    if year_array.ndim != 1 or year_array.size == 0:
        raise ValueError("years debe ser una secuencia unidimensional no vacía.")
    if np.unique(year_array).size != year_array.size:
        raise ValueError("years no puede contener años duplicados.")
    if np.any(np.diff(year_array) <= 0):
        raise ValueError("years debe estar ordenado estrictamente de forma ascendente.")
    if not components:
        raise ValueError("Se requiere al menos un componente.")

    names = tuple(components.keys())
    columns: list[FloatArray] = []
    for name in names:
        values = np.asarray(components[name], dtype=float)
        if values.ndim != 1 or values.size != year_array.size:
            raise ValueError(f"El componente {name!r} debe tener un valor por año.")
        finite = values[np.isfinite(values)]
        if np.any((finite < 0.0) | (finite > 1.0)):
            raise ValueError(f"El componente {name!r} debe estar normalizado en [0, 1].")
        columns.append(values)

    matrix = np.column_stack(columns)
    return year_array, names, matrix


def _validated_weights(
    names: tuple[str, ...], weights: Mapping[str, float] | None
) -> FloatArray:
    if weights is None:
        return np.full(len(names), 1.0 / len(names), dtype=float)
    if set(weights) != set(names):
        raise ValueError("Los pesos deben contener exactamente los nombres de los componentes.")

    vector = np.asarray([weights[name] for name in names], dtype=float)
    if not np.all(np.isfinite(vector)) or np.any(vector < 0.0):
        raise ValueError("Los pesos deben ser finitos y no negativos.")
    total = float(vector.sum())
    if total <= 0.0:
        raise ValueError("La suma de los pesos debe ser positiva.")
    return vector / total


def _aggregate(matrix: FloatArray, weights: FloatArray) -> tuple[FloatArray, FloatArray]:
    complete = np.all(np.isfinite(matrix), axis=1)
    arithmetic = np.full(matrix.shape[0], np.nan, dtype=float)
    geometric = np.full(matrix.shape[0], np.nan, dtype=float)
    if np.any(complete):
        valid = matrix[complete]
        arithmetic[complete] = valid @ weights
        # El producto ponderado gestiona ceros sin aplicar log(0).
        geometric[complete] = np.prod(np.power(valid, weights), axis=1)
    return arithmetic, geometric


def build_resource_indices(
    years: Sequence[int] | NDArray[np.integer],
    components: Mapping[str, Sequence[float] | NDArray[np.floating]],
    *,
    weights: Mapping[str, float] | None = None,
) -> ResourceIndexResult:
    """Calcula medias aritmética y geométrica con pesos normalizados.

    Los años con cualquier componente ausente reciben NaN en ambos índices.
    No hay imputación ni renormalización anual de pesos.
    """
    year_array, names, matrix = _validate_components(years, components)
    weight_vector = _validated_weights(names, weights)
    arithmetic, geometric = _aggregate(matrix, weight_vector)
    complete = np.all(np.isfinite(matrix), axis=1)
    return ResourceIndexResult(
        years=year_array,
        component_names=names,
        components=matrix,
        weights=weight_vector,
        arithmetic=arithmetic,
        geometric=geometric,
        complete=complete,
    )


def sample_weight_sensitivity(
    years: Sequence[int] | NDArray[np.integer],
    components: Mapping[str, Sequence[float] | NDArray[np.floating]],
    *,
    n_samples: int = 2_000,
    concentration: float = 1.0,
    seed: int = 42,
) -> WeightSensitivityResult:
    """Propaga incertidumbre de ponderación mediante una distribución Dirichlet.

    concentration=1 produce una distribución uniforme sobre el simplex de pesos.
    Valores mayores concentran los pesos alrededor de la combinación equiponderada;
    valores menores generan combinaciones más extremas. No representa incertidumbre
    estadística de los datos, sino sensibilidad a la elección de ponderaciones.
    """
    if n_samples < 1:
        raise ValueError("n_samples debe ser al menos 1.")
    if not np.isfinite(concentration) or concentration <= 0.0:
        raise ValueError("concentration debe ser positiva y finita.")

    year_array, names, matrix = _validate_components(years, components)
    if not np.any(np.all(np.isfinite(matrix), axis=1)):
        raise ValueError("Se necesita al menos un año con todos los componentes disponibles.")
    rng = np.random.default_rng(seed)
    weight_samples = rng.dirichlet(
        np.full(len(names), concentration, dtype=float), size=n_samples
    )

    arithmetic_samples = np.full((n_samples, year_array.size), np.nan, dtype=float)
    geometric_samples = np.full_like(arithmetic_samples, np.nan)
    for index, weights in enumerate(weight_samples):
        arithmetic, geometric = _aggregate(matrix, weights)
        arithmetic_samples[index] = arithmetic
        geometric_samples[index] = geometric

    arithmetic_quantiles = np.nanquantile(
        arithmetic_samples, [0.05, 0.50, 0.95], axis=0
    )
    geometric_quantiles = np.nanquantile(
        geometric_samples, [0.05, 0.50, 0.95], axis=0
    )
    return WeightSensitivityResult(
        component_names=names,
        weight_samples=weight_samples,
        arithmetic_samples=arithmetic_samples,
        geometric_samples=geometric_samples,
        arithmetic_quantiles=arithmetic_quantiles,
        geometric_quantiles=geometric_quantiles,
    )
