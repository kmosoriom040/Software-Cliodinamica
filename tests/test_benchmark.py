import pytest

pytest.importorskip("sklearn")
pytest.importorskip("pandas")

from cliodinamica.ml import FEATURE_COLUMNS  # noqa: E402
from cliodinamica.ml.benchmark import compare_models, permutation_importances  # noqa: E402
from cliodinamica.ml.dataset import generate_dataset  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return generate_dataset(500, seed=0, t_end=400, n_points=101)


def test_comparacion_de_modelos(df):
    res = compare_models(df, FEATURE_COLUMNS, cv=3)
    assert set(res) == {"MLP", "Random Forest", "Regresión logística"}
    assert all(0.0 <= m <= 1.0 for m, _ in res.values())
    assert res["Random Forest"][0] > 0.8


def test_importancias_ordenadas(df):
    imp = permutation_importances(df, FEATURE_COLUMNS, n_repeats=3)
    medias = [m for m, _ in imp.values()]
    assert medias == sorted(medias, reverse=True)
    assert set(imp) == set(FEATURE_COLUMNS)
