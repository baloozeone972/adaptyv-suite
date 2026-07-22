"""Tests for the Langmuir model primitives."""

from __future__ import annotations

import numpy as np
from adaptyv_kinetics.models.langmuir import infer_assoc_end, response


def test_response_starts_at_baseline() -> None:
    r = response(np.array([0.0]), 1e5, 1e-3, 0.8, 1e-8, 120.0, baseline=0.05)
    assert abs(r[0] - 0.05) < 1e-9


def test_response_monotone_association() -> None:
    t = np.linspace(0, 120, 50)
    r = response(t, 1e5, 1e-3, 0.8, 5e-8, 120.0)
    assert np.all(np.diff(r) >= -1e-12)  # non-decreasing during association


def test_response_decays_in_dissociation() -> None:
    t = np.array([120.0, 240.0, 480.0])
    r = response(t, 1e5, 1e-3, 0.8, 5e-8, 120.0)
    assert r[2] < r[0]


def test_infer_assoc_end_smoothed() -> None:
    t = np.linspace(0, 200, 101)
    y = np.concatenate([np.linspace(0, 1, 51), np.linspace(1, 0.5, 50)])
    y[70] = 5.0  # a stray spike must not fool the split point
    assert 90.0 <= infer_assoc_end(t, y) <= 110.0
