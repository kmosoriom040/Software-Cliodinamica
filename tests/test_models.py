import numpy as np

from cliodinamica.core import create_model


def test_equilibrio_anula_las_derivadas():
    m = create_model("cliodinamica")
    p = m.default_params()
    y_eq = m.equilibrium(p)
    assert np.allclose(m.rhs(0.0, y_eq, p), 0.0, atol=1e-12)


def test_sin_poblacion_no_hay_crecimiento():
    m = create_model("cliodinamica")
    p = m.default_params()
    dy = m.rhs(0.0, np.array([0.0, 1.0, 0.0, 1.0]), p)
    assert dy[0] == 0.0
