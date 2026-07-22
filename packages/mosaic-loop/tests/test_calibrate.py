"""Tests for the correlation helpers and the calibration/drift analysis."""

from __future__ import annotations

import numpy as np
from mosaic_loop.calibrate import analyze, calibrate_term
from mosaic_loop.data import synthetic_measurements
from mosaic_loop.schemas import DesignMeasurement, ObjectiveTerm
from mosaic_loop.stats import pearson, spearman


def test_pearson_spearman() -> None:
    a = np.array([1.0, 2.0, 3.0, 4.0])
    assert pearson(a, a) == 1.0
    assert spearman(a, a[::-1]) == -1.0
    assert pearson(a, np.array([5.0, 5.0, 5.0, 5.0])) == 0.0  # zero variance
    assert spearman(np.array([1.0]), np.array([1.0])) == 0.0


def test_calibrate_recovers_linear_relation() -> None:
    ms = [
        DesignMeasurement(
            name=f"d{i}",
            predicted={ObjectiveTerm.AFFINITY: float(i)},
            measured={ObjectiveTerm.AFFINITY: 3.0 * i + 2.0},
        )
        for i in range(10)
    ]
    cal = calibrate_term(ms, ObjectiveTerm.AFFINITY)
    assert abs(cal.slope - 3.0) < 1e-6
    assert abs(cal.intercept - 2.0) < 1e-6
    assert cal.spearman > 0.999
    assert cal.drift < 1e-3


def test_calibrate_single_point_is_safe() -> None:
    ms = [
        DesignMeasurement(
            name="d",
            predicted={ObjectiveTerm.AFFINITY: 1.0},
            measured={ObjectiveTerm.AFFINITY: 5.0},
        )
    ]
    cal = calibrate_term(ms, ObjectiveTerm.AFFINITY)
    assert cal.n == 1
    assert cal.slope == 0.0  # cannot fit a line from one point


def test_synthetic_drift_pattern() -> None:
    report = analyze(synthetic_measurements(n=120, seed=0))
    by_term = {c.term: c for c in report.calibrations}
    # affinity tracks reality; stability is a poor proxy by construction
    assert by_term[ObjectiveTerm.AFFINITY].spearman > 0.8
    assert by_term[ObjectiveTerm.STABILITY].drift > 0.7


def test_recalibration_improves_objective_agreement() -> None:
    report = analyze(synthetic_measurements(n=150, seed=1))
    assert report.objective_agreement_calibrated >= report.objective_agreement_raw
