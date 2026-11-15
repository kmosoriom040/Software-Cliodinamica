import numpy as np
import pytest

from cliodinamica.analysis import (
    analyze_equilibrium,
    elasticities,
    jacobian,
    regime_map,
    run_ensemble,
    sweep_1d,
)
from cliodinamica.core import create_model


class _Lineal:
    state_names = ("a", "b")

    def __init__(self, A):
        self.A = np.asarray(A, float)

    def rhs(self, t, y, p):
        return self.A @ y


def test_jacobiano_de_un_sistema_lineal():
    A = [[-1.0, 2.0], [0.5, -3.0]]
    assert np.allclose(jacobian(_Lineal(A), [0.3, 0.7], None), A, atol=1e-6)


def test_equilibrio_de_cliodinamica_es_estable():
    m = create_model("cliodinamica")
    rep = analyze_equilibrium(m, m.default_params())
    assert rep.stable and rep.kind.startswith("estable")
    assert np.all(rep.eigenvalues.real < 0)


def test_lotka_volterra_es_un_centro():
    m = create_model("lotka_volterra")
    p = m.default_params()
    rep = analyze_equilibrium(m, p)
    assert rep.kind.startswith("marginal")
    assert np.allclose(np.abs(rep.eigenvalues.imag), np.sqrt(p.a * p.c), rtol=1e-4)


def test_signos_de_las_elasticidades():
    m = create_model("cliodinamica")
    el = elasticities(m, m.default_params())
    assert el["lam"]["S"] < 0 < el["sigma"]["S"]
    assert el["kappa"]["N"] > 0


def test_barrido_estabilidad_decrece_con_lambda():
    m = create_model("cliodinamica")
    sw = sweep_1d(m, m.default_params(), "lam", np.linspace(0.05, 1.0, 8), t_end=500)
    s = sw.final[:, sw.state_names.index("S")]
    assert np.all(np.diff(s) <= 1e-9)
    assert sw.labels[-1] == "colapso" and sw.labels[0] != "colapso"


def test_mapa_de_regimenes():
    m = create_model("cliodinamica")
    rm = regime_map(m, m.default_params(), "lam", [0.05, 1.0], "gamma", [0.005, 0.02],
                    t_end=400, n_points=101)
    assert rm.labels.shape == (2, 2)
    assert sum(rm.class_fractions().values()) == pytest.approx(1.0)
    assert np.all(rm.labels[:, 1] == 2)  # lambda alto: colapso


def test_mapa_rechaza_parametros_repetidos_o_desconocidos():
    m = create_model("cliodinamica")
    with pytest.raises(ValueError):
        regime_map(m, m.default_params(), "lam", [0.1], "lam", [0.1])
    with pytest.raises(ValueError):
        sweep_1d(m, m.default_params(), "nada", [0.1])


def test_ensamble():
    m = create_model("cliodinamica")
    ens = run_ensemble(m, m.default_params(), n_runs=30, rel_sigma=0.1, t_end=200, n_points=101)
    assert ens.y.shape == (30, 4, 101)
    assert sum(ens.class_probabilities().values()) == pytest.approx(1.0)
    p5, _, p50, _, p95 = ens.percentiles("N")
    assert np.all(p5 <= p50 + 1e-12) and np.all(p50 <= p95 + 1e-12)


def test_ensamble_sin_ruido_es_determinista():
    m = create_model("cliodinamica")
    ens = run_ensemble(m, m.default_params(), n_runs=5, rel_sigma=0.0, t_end=100, n_points=51)
    assert np.allclose(ens.y, ens.y[0])
