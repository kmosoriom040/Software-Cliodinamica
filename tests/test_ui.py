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


def test_nuevas_pestañas_y_calculos():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception
    assert len(at.tabs) == 7
    at.slider(key="reg_n").set_value(8)
    at.slider(key="ens_n").set_value(20)
    at.button(key="btn_regime").click().run()
    assert not at.exception
    at.button(key="btn_sweep").click().run()
    assert not at.exception
    at.button(key="btn_ens").click().run()
    assert not at.exception


def test_figuras_de_analisis():
    from cliodinamica.analysis import regime_map, run_ensemble, sweep_1d

    m = create_model("cliodinamica")
    p = m.default_params()
    rm = regime_map(m, p, "lam", [0.1, 0.9], "gamma", [0.01, 0.03], t_end=200, n_points=51)
    assert len(plots.regime_map_fig(rm, (0.2, 0.02)).data) == 2
    sw = sweep_1d(m, p, "lam", [0.1, 0.5, 0.9], t_end=200, n_points=51)
    assert len(plots.bifurcation_fig(sw, "S").data) == 3
    ens = run_ensemble(m, p, n_runs=10, t_end=100, n_points=51)
    assert len(plots.fan_chart_fig(ens, "N").data) == 5
    assert len(plots.probabilities_fig(ens.class_probabilities()).data) == 1
