"""Series nacionales observadas y alineación temporal de indicadores."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class IndicatorSeries:
    """Serie anual con procedencia explícita."""

    name: str
    years: IntArray
    values: FloatArray
    unit: str
    source: str
    source_url: str
    methodology: str
    higher_is_better: bool

    def __post_init__(self) -> None:
        years = np.asarray(self.years, dtype=np.int64)
        values = np.asarray(self.values, dtype=float)
        if not self.name.strip():
            raise ValueError("El nombre del indicador no puede estar vacío.")
        if years.ndim != 1 or values.ndim != 1 or years.size != values.size:
            raise ValueError("years y values deben ser vectores de igual longitud.")
        if years.size == 0 or np.unique(years).size != years.size:
            raise ValueError("La serie debe contener años únicos y no estar vacía.")
        if np.any(np.diff(years) <= 0):
            raise ValueError("Los años deben estar ordenados de forma ascendente.")
        if not self.unit.strip() or not self.source.strip() or not self.methodology.strip():
            raise ValueError("Unidad, fuente y metodología son metadatos obligatorios.")
        if not np.all(np.isfinite(values) | np.isnan(values)):
            raise ValueError("La serie solo puede contener números finitos o NaN.")
        object.__setattr__(self, "years", years)
        object.__setattr__(self, "values", values)


def load_indicator_csv(
    path: str | Path,
    *,
    name: str,
    unit: str,
    source: str,
    source_url: str,
    methodology: str,
    higher_is_better: bool,
) -> IndicatorSeries:
    """Lee un CSV UTF-8 con columnas obligatorias year,value.

    Los valores vacíos se convierten en NaN. No se interpolan ni imputan.
    """
    rows: list[tuple[int, float]] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or not {"year", "value"}.issubset(reader.fieldnames):
            raise ValueError("El CSV debe contener las columnas year y value.")
        for line_number, row in enumerate(reader, start=2):
            try:
                year = int(row["year"])
                raw_value = (row["value"] or "").strip()
                value = float(raw_value) if raw_value else float("nan")
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Fila {line_number}: year/value no válidos.") from exc
            if not np.isfinite(value) and not np.isnan(value):
                raise ValueError(f"Fila {line_number}: value debe ser finito o estar vacío.")
            rows.append((year, value))

    rows.sort(key=lambda item: item[0])
    years = np.asarray([row[0] for row in rows], dtype=np.int64)
    values = np.asarray([row[1] for row in rows], dtype=float)
    return IndicatorSeries(
        name=name,
        years=years,
        values=values,
        unit=unit,
        source=source,
        source_url=source_url,
        methodology=methodology,
        higher_is_better=higher_is_better,
    )


def align_indicator_series(
    indicators: Mapping[str, IndicatorSeries],
) -> tuple[IntArray, dict[str, FloatArray]]:
    """Alinea indicadores por intersección exacta de años observados.

    No completa años faltantes, no extrapola y no interpola. Los valores NaN
    permanecen explícitos para que el cálculo posterior del índice los detecte.
    """
    if not indicators:
        raise ValueError("Se requiere al menos un indicador.")
    year_sets = [set(series.years.tolist()) for series in indicators.values()]
    common_years = sorted(set.intersection(*year_sets))
    if not common_years:
        raise ValueError("Los indicadores no comparten ningún año.")
    years = np.asarray(common_years, dtype=np.int64)
    aligned: dict[str, FloatArray] = {}
    for name, series in indicators.items():
        lookup = dict(zip(series.years.tolist(), series.values.tolist(), strict=True))
        aligned[name] = np.asarray([lookup[year] for year in common_years], dtype=float)
    return years, aligned


def available_year_range(indicators: Iterable[IndicatorSeries]) -> dict[str, tuple[int, int]]:
    """Devuelve el rango de años disponible para cada indicador."""
    return {
        indicator.name: (int(indicator.years[0]), int(indicator.years[-1]))
        for indicator in indicators
    }
