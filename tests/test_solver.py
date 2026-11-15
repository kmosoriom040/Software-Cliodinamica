import numpy as np
import pytest

from cliodinamica.core import create_model, simulate


def test_forma_de_la_trayectoria():
    m = create_model("cliodinamica")
    tray = simulate(m, t_end=100, n_points=101)
    assert tray.y.shape == (4, 101)
    assert tray.t[0] == 0.0 and tray.t[-1] == pytest.approx(100.0)


def test_desigualdad_y_estabilidad_acotadas():
    tray = simulate(create_model("cliodinamica"), t_end=500)
    for nombre in ("G", "S"):
        serie = tray.series(nombre)
        assert serie.min() >= -1e-9 and serie.max() <= 1 + 1e-9


def test_converge_al_equilibrio():
    m = create_model("cliodinamica")
    tray = simulate(m, t_end=3000, n_points=301)
    assert np.allclose(tray.y[:, -1], m.equilibrium(m.default_params()), atol=1e-2)


def test_lotka_volterra_conserva_la_cantidad_hamiltoniana():
    m = create_model("lotka_volterra")
    p = m.default_params()
    tray = simulate(m, p, t_end=200, n_points=401)
    x, y = tray.series("x"), tray.series("y")
    h = p.d * x - p.c * np.log(x) + p.b * y - p.a * np.log(y)
    assert np.allclose(h, h[0], rtol=1e-6)


def test_estado_inicial_invalido():
    m = create_model("cliodinamica")
    with pytest.raises(ValueError):
        simulate(m, y0=[1.0, 1.0])
    with pytest.raises(ValueError):
        simulate(m, y0=[-1.0, 1.0, 0.0, 1.0])
