"""Tests for the delegation analysis."""

from __future__ import annotations

import numpy as np
from sensorgram_triage.delegation import delegation_curve, grouped_split
from sensorgram_triage.labels import Dataset
from sensorgram_triage.model import LogisticModel
from sensorgram_triage.schemas import DelegationCurve


def test_grouped_split_is_stratified() -> None:
    groups = ["a", "a", "b", "c", "d", "d"]
    y = np.array([1.0, 1.0, 0.0, 0.0, 1.0, 1.0])
    train, test = grouped_split(groups, y, test_fraction=0.5)
    test_labels = set(y[test].tolist())
    assert test_labels == {0.0, 1.0}  # both classes present in the test split
    assert not (train & test).any()  # disjoint


def test_delegation_curve_operating_point() -> None:
    y = np.array([0.0, 0.0, 1.0, 1.0])
    probs = np.array([0.1, 0.2, 0.8, 0.9])
    curve = delegation_curve(y, probs)
    op = curve.operating_point(0.0)
    assert op.false_negative_rate == 0.0
    assert op.auto_approved_fraction >= 0.5
    assert curve.brier_score < 0.05


def test_operating_point_falls_back_when_no_point_meets_fnr() -> None:
    y = np.array([1.0, 1.0])
    probs = np.array([0.0, 0.0])  # both positives always auto-approved -> FNR high everywhere
    curve = delegation_curve(y, probs)
    op = curve.operating_point(-1.0)  # impossible target
    assert op is not None


def test_calibrate_is_meaningful(calibrated: tuple[LogisticModel, DelegationCurve]) -> None:
    _model, curve = calibrated
    assert curve.n > 0
    op = curve.operating_point(0.05)
    assert 0.0 < op.auto_approved_fraction <= 1.0


def test_dataset_fixture_shape(dataset: Dataset) -> None:
    assert dataset.x.ndim == 2
