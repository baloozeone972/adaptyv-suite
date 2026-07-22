"""Tests for the learning-curve fit and the honest verdicts."""

from __future__ import annotations

from boltz_tune.curve import evaluate, fit_curve
from boltz_tune.data import BASE_SCORE, synthetic_sweep
from boltz_tune.schemas import LearningCurve


def test_fit_recovers_plateau() -> None:
    curve = fit_curve(synthetic_sweep(seed=0))
    assert 0.69 < curve.plateau < 0.75  # true plateau is 0.72
    assert curve.predict(50) < curve.predict(1600)  # more data, higher score


def test_n_for_reachable_and_not() -> None:
    curve = LearningCurve(plateau=0.72, coef=0.9, alpha=0.5)
    assert curve.n_for(0.70) is not None
    assert curve.n_for(0.72) is None  # equal to plateau: unreachable
    assert curve.n_for(0.80) is None  # above plateau: unreachable


def test_verdict_already_helps() -> None:
    r = evaluate(synthetic_sweep(seed=0), base_score=BASE_SCORE, target_lift=0.02)
    assert "already helps" in r.verdict
    assert r.current_lift > 0


def test_verdict_needs_more_data() -> None:
    r = evaluate(synthetic_sweep(seed=0), base_score=BASE_SCORE, target_lift=0.05)
    assert "more data" in r.verdict
    assert r.is_finite_multiple()
    assert r.data_multiple is not None and r.data_multiple > 1.0


def test_verdict_unreachable_above_plateau() -> None:
    r = evaluate(synthetic_sweep(seed=0), base_score=BASE_SCORE, target_lift=0.10)
    assert "unreachable" in r.verdict
    assert r.n_for_target is None


def test_verdict_never_beats_base() -> None:
    r = evaluate(synthetic_sweep(seed=0), base_score=0.80, target_lift=0.05)
    assert "does not beat the base model" in r.verdict
