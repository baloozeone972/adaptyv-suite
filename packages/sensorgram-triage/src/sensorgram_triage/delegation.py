"""The delegation analysis — the project's central figure.

Not "what accuracy does the model reach" but "how many curves can be auto-approved
without a human eye, at a given false-negative rate". Evaluated on a held-out split
grouped by protein, so replicates of the same protein never leak across train/test.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from sensorgram_triage.labels import synthetic_dataset
from sensorgram_triage.model import LogisticModel
from sensorgram_triage.schemas import DelegationCurve, DelegationPoint

Array = NDArray[np.float64]


def grouped_split(groups: list[str], y: Array, test_fraction: float = 0.4) -> tuple[Array, Array]:
    """Deterministic split into train/test masks, grouped by name and stratified.

    Stratifying by class matters: without it, a class-sorted set of group names can
    put every problematic protein on one side, making the delegation curve trivial.
    """
    label_of: dict[str, float] = {}
    for group, label in zip(groups, y, strict=True):
        label_of[group] = max(label_of.get(group, 0.0), label)
    test_names: set[str] = set()
    for cls in (0.0, 1.0):
        names = sorted(g for g in set(groups) if label_of[g] == cls)
        n_test = max(1, round(len(names) * test_fraction))
        test_names.update(names[::-1][:n_test])
    is_test = np.array([g in test_names for g in groups])
    return ~is_test, is_test


def delegation_curve(y_true: Array, probs: Array, n_thresholds: int = 101) -> DelegationCurve:
    """Build the auto-approve-fraction vs false-negative-rate curve."""
    positives = y_true == 1.0
    points: list[DelegationPoint] = []
    for threshold in np.linspace(0.0, 1.0, n_thresholds):
        approved = probs < threshold  # auto-approved = predicted "clean enough"
        fnr = float(approved[positives].mean()) if positives.any() else 0.0
        points.append(
            DelegationPoint(
                threshold=float(threshold),
                auto_approved_fraction=float(approved.mean()),
                false_negative_rate=fnr,
            )
        )
    brier = float(np.mean((probs - y_true) ** 2))
    return DelegationCurve(points=points, brier_score=brier, n=int(y_true.size))


def calibrate(
    n_good: int = 14, n_bad: int = 10, seed: int = 0
) -> tuple[LogisticModel, DelegationCurve]:
    """End-to-end: generate a labelled set, fit on train, score the held-out split."""
    data = synthetic_dataset(n_good=n_good, n_bad=n_bad, seed=seed)
    train, test = grouped_split(data.groups, data.y)
    model = LogisticModel.fit(data.x[train], data.y[train])
    probs = model.predict_proba(data.x[test])
    return model, delegation_curve(data.y[test], probs)
