import pytest

from cliodinamica.core import available_models, create_model


def test_modelos_disponibles():
    assert {"cliodinamica", "lotka_volterra"} <= set(available_models())


def test_crear_modelo_por_nombre():
    assert create_model("cliodinamica").name == "cliodinamica"


def test_modelo_desconocido():
    with pytest.raises(ValueError, match="desconocido"):
        create_model("no_existe")
