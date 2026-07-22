"""Tests for the numpy logistic regression."""

from __future__ import annotations

import numpy as np
from sensorgram_triage.model import LogisticModel


def test_separates_two_clusters() -> None:
    x = np.array([[0.0, 0.0], [0.1, -0.1], [5.0, 5.0], [4.9, 5.1]])
    y = np.array([0.0, 0.0, 1.0, 1.0])
    model = LogisticModel.fit(x, y)
    probs = model.predict_proba(x)
    assert probs[0] < 0.5 < probs[2]


def test_deterministic() -> None:
    x = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 0.0, 1.0, 1.0])
    a = LogisticModel.fit(x, y).predict_proba(x)
    b = LogisticModel.fit(x, y).predict_proba(x)
    assert np.allclose(a, b)


def test_constant_feature_does_not_crash() -> None:
    x = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0], [1.0, 3.0]])  # first column constant
    y = np.array([0.0, 0.0, 1.0, 1.0])
    probs = LogisticModel.fit(x, y).predict_proba(x)
    assert np.all(np.isfinite(probs))


def test_probabilities_in_unit_interval() -> None:
    x = np.array([[-100.0], [100.0]])
    y = np.array([0.0, 1.0])
    probs = LogisticModel.fit(x, y).predict_proba(x)
    assert np.all((probs >= 0.0) & (probs <= 1.0))
