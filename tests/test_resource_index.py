import numpy as np
import pytest

from cliodinamica.data import (
    build_resource_indices,
    normalize_indicator,
    sample_weight_sensitivity,
)


def test_normalize_indicator_uses_fixed_reference_bounds():
    result = normalize_indicator(
        [10.0, 15.0, 20.0, np.nan],
        lower_bound=10.0,
        upper_bound=20.0,
    )
    assert np.allclose(result[:3], [0.0, 0.5, 1.0])
    assert np.isnan(result[3])


def test_normalize_indicator_reverses_pressure_direction():
    result = normalize_indicator(
        [0.0, 5.0, 10.0],
        lower_bound=0.0,
        upper_bound=10.0,
        higher_is_better=False,
    )
    assert np.allclose(result, [1.0, 0.5, 0.0])


def test_normalize_indicator_rejects_invalid_bounds():
    with pytest.raises(ValueError):
        normalize_indicator([1.0], lower_bound=2.0, upper_bound=2.0)


def test_builds_both_indices_with_equal_weights():
    result = build_resource_indices(
        [2000, 2001],
        {
            "forest": [1.0, 0.25],
            "water": [1.0, 1.0],
        },
    )
    assert np.allclose(result.weights, [0.5, 0.5])
    assert np.allclose(result.arithmetic, [1.0, 0.625])
    assert np.allclose(result.geometric, [1.0, 0.5])


def test_missing_component_is_not_imputed_or_reweighted():
    result = build_resource_indices(
        [2000, 2001],
        {
            "forest": [0.5, np.nan],
            "water": [0.5, 1.0],
        },
    )
    assert result.complete.tolist() == [True, False]
    assert result.arithmetic[0] == pytest.approx(0.5)
    assert np.isnan(result.arithmetic[1])
    assert np.isnan(result.geometric[1])


def test_custom_weights_are_normalized():
    result = build_resource_indices(
        [2000],
        {"forest": [1.0], "water": [0.0]},
        weights={"forest": 3.0, "water": 1.0},
    )
    assert np.allclose(result.weights, [0.75, 0.25])
    assert result.arithmetic[0] == pytest.approx(0.75)


def test_rejects_weights_for_different_components():
    with pytest.raises(ValueError):
        build_resource_indices(
            [2000], {"forest": [0.5], "water": [0.5]}, weights={"forest": 1.0}
        )


def test_weight_sensitivity_is_reproducible_and_bounded():
    components = {
        "forest": [0.2, 0.8],
        "water": [0.9, 0.4],
    }
    first = sample_weight_sensitivity([2000, 2001], components, n_samples=100, seed=7)
    second = sample_weight_sensitivity([2000, 2001], components, n_samples=100, seed=7)
    assert np.allclose(first.weight_samples, second.weight_samples)
    assert np.allclose(first.arithmetic_samples, second.arithmetic_samples)
    assert first.arithmetic_quantiles.shape == (3, 2)
    assert first.geometric_quantiles.shape == (3, 2)
    assert np.all((first.arithmetic_samples >= 0.0) & (first.arithmetic_samples <= 1.0))
    assert np.all((first.geometric_samples >= 0.0) & (first.geometric_samples <= 1.0))


def test_years_must_be_strictly_increasing():
    with pytest.raises(ValueError):
        build_resource_indices([2001, 2000], {"forest": [0.2, 0.3]})


def test_weight_sensitivity_requires_at_least_one_complete_year():
    with pytest.raises(ValueError):
        sample_weight_sensitivity(
            [2000, 2001],
            {"forest": [np.nan, np.nan], "water": [0.2, 0.3]},
            n_samples=10,
        )
