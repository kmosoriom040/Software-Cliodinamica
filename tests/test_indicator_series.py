import numpy as np
import pytest

from cliodinamica.data.series import (
    IndicatorSeries,
    align_indicator_series,
    load_indicator_csv,
)


def make_series(name, years, values):
    return IndicatorSeries(
        name=name,
        years=np.asarray(years),
        values=np.asarray(values, dtype=float),
        unit="km2",
        source="DANE",
        source_url="https://www.dane.gov.co/",
        methodology="Serie anual de ejemplo",
        higher_is_better=True,
    )


def test_aligns_only_common_years(tmp_path):
    forests = make_series("forests", [2000, 2001, 2002], [10, 11, 12])
    water = make_series("water", [2001, 2002, 2003], [20, 21, 22])
    years, aligned = align_indicator_series({"forests": forests, "water": water})
    assert years.tolist() == [2001, 2002]
    assert np.allclose(aligned["forests"], [11, 12])
    assert np.allclose(aligned["water"], [20, 21])


def test_alignment_fails_without_common_years():
    forests = make_series("forests", [2000], [10])
    water = make_series("water", [2001], [20])
    with pytest.raises(ValueError):
        align_indicator_series({"forests": forests, "water": water})


def test_load_indicator_csv_keeps_missing_values(tmp_path):
    path = tmp_path / "forest.csv"
    path.write_text("year,value\n2000,10.5\n2001,\n", encoding="utf-8")
    series = load_indicator_csv(
        path,
        name="forest_area",
        unit="km2",
        source="DANE",
        source_url="https://www.dane.gov.co/",
        methodology="Ejemplo de prueba",
        higher_is_better=True,
    )
    assert series.years.tolist() == [2000, 2001]
    assert series.values[0] == pytest.approx(10.5)
    assert np.isnan(series.values[1])


def test_indicator_series_rejects_duplicate_years():
    with pytest.raises(ValueError):
        make_series("forests", [2000, 2000], [10, 11])
