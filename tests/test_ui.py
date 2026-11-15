from pathlib import Path

import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")
pytest.importorskip("pandas")

from streamlit.testing.v1 import AppTest  # noqa: E402

import cliodinamica.ui  # noqa: E402
from cliodinamica.core import create_model, simulate  # noqa: E402
from cliodinamica.ui import plots  # noqa: E402

APP = str(Path(cliodinamica.ui.__file__).with_name("app.py"))


def _tray():
    return simulate(create_model("cliodinamica"), t_end=100, n_points=101)


def test_series_de_tiempo_tiene_cuatro_curvas():
    assert len(plots.timeseries_fig(_tray()).data) == 4


def test_plano_NR_incluye_campo_y_nulclinas():
    m = create_model("cliodinamica")
    fig = plots.phase2d_fig(_tray(), "N", "R", model=m, params=m.default_params())
    nombres = {t.name for t in fig.data}
    assert {"dN/dt = 0", "dR/dt = 0", "Equilibrio", "Trayectoria"} <= nombres


def test_fase_3d():
    fig = plots.phase3d_fig(_tray())
    assert len(fig.data) == 3


def test_la_app_arranca_sin_errores():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value == "crecimiento"


def test_preset_de_colapso_cambia_la_clase():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.selectbox(key="preset").select("Colapso por desigualdad").run()
    assert not at.exception
    assert at.metric[0].value == "colapso"
