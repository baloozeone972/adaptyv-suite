"""Tests for the shared statistics primitives."""

from __future__ import annotations

import numpy as np
import pytest
from adaptyv_core.stats import bootstrap_ci


def test_constant_data_zero_width_ci() -> None:
    est = bootstrap_ci([2.0, 2.0, 2.0], n_resamples=50)
    assert est.value == 2.0
    assert est.ci_low == est.ci_high == 2.0
    assert est.n == 3


def test_ci_brackets_mean() -> None:
    rng = np.random.default_rng(0)
    est = bootstrap_ci(rng.normal(10.0, 1.0, 200), n_resamples=500)
    assert est.ci_low < est.value < est.ci_high
    assert abs(est.value - 10.0) < 0.5


def test_empty_raises() -> None:
    with pytest.raises(ValueError):
        bootstrap_ci([])


def test_as_tuple() -> None:
    assert bootstrap_ci([1.0, 1.0], n_resamples=10).as_tuple() == (1.0, 1.0, 1.0)
