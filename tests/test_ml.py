import numpy as np
import pytest

pytest.importorskip("sklearn")
pytest.importorskip("pandas")

from cliodinamica.core import Trajectory  # noqa: E402
from cliodinamica.ml import FEATURE_COLUMNS, extract_features, label_trajectory  # noqa: E402
from cliodinamica.ml.classifier import StateClassifier, evaluate  # noqa: E402
from cliodinamica.ml.dataset import INPUT_COLUMNS, generate_dataset  # noqa: E402


def _tray(n, s, g=None):
    n = np.asarray(n, float)
    s = np.asarray(s, float)
    g = np.full_like(n, 0.5) if g is None else np.asarray(g, float)
    t = np.arange(len(n), dtype=float)
    y = np.vstack([n, np.ones_like(n), g, s])
    return Trajectory(t=t, y=y, state_names=("N", "R", "G", "S"))


def test_etiqueta_colapso_por_estabilidad():
    assert label_trajectory(_tray([1, 1.5, 2], [0.9, 0.5, 0.1])) == "colapso"


def test_etiqueta_colapso_por_caida_de_poblacion():
    assert label_trajectory(_tray([1, 2, 0.5], [0.9, 0.9, 0.9])) == "colapso"


def test_etiqueta_crecimiento_y_estancamiento():
    assert label_trajectory(_tray([1, 1.2, 1.5], [0.9, 0.9, 0.9])) == "crecimiento"
    assert label_trajectory(_tray([1, 1.02, 1.05], [0.9, 0.9, 0.9])) == "estancamiento"


def test_rasgos():
    f = extract_features(_tray([1, 2, 1.5], [0.9, 0.5, 0.6]))
    assert set(f) == set(FEATURE_COLUMNS)
    assert f["delta"] == pytest.approx(0.5)
    assert f["n_max_ratio"] == pytest.approx(2.0)


def test_dataset_reproducible_y_con_columnas():
    a = generate_dataset(30, seed=1, t_end=200, n_points=101)
    b = generate_dataset(30, seed=1, t_end=200, n_points=101)
    assert a.equals(b)
    assert set(INPUT_COLUMNS) | set(FEATURE_COLUMNS) | {"label"} <= set(a.columns)


def test_clasificador_entrena_y_guarda(tmp_path):
    df = generate_dataset(1000, seed=0, t_end=500, n_points=126)
    clf, m = evaluate(df, FEATURE_COLUMNS, seed=0)
    assert m["accuracy"] > 0.8
    ruta = tmp_path / "clf.joblib"
    clf.save(ruta)
    cargado = StateClassifier.load(ruta)
    assert list(cargado.predict(df[list(FEATURE_COLUMNS)])) == list(
        clf.predict(df[list(FEATURE_COLUMNS)])
    )
