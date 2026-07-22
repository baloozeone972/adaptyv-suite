"""Fit and reason about the learning curve."""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit

from boltz_tune.schemas import LearningCurve, TrainingObservation, TuneResult


def _model(n: np.ndarray, plateau: float, coef: float, alpha: float) -> np.ndarray:
    return plateau - coef * n ** (-alpha)


def fit_curve(observations: list[TrainingObservation]) -> LearningCurve:
    """Fit score(n) = plateau - coef·n^(-alpha) by least squares."""
    n = np.array([o.n_train for o in observations], dtype=np.float64)
    y = np.array([o.score for o in observations], dtype=np.float64)
    p0 = [float(y.max()) + 0.02, 1.0, 0.5]
    bounds = ([float(y.max()), 1e-3, 0.05], [1.0, 100.0, 2.0])
    params, _ = curve_fit(_model, n, y, p0=p0, bounds=bounds, maxfev=10000)
    return LearningCurve(plateau=float(params[0]), coef=float(params[1]), alpha=float(params[2]))


def _verdict(
    curve: LearningCurve,
    base: float,
    current_score: float,
    target: float,
    n_target: float | None,
    current_n: int,
) -> str:
    if curve.plateau <= base:
        return (
            "fine-tuning does not beat the base model at any data volume (domain shift dominates)"
        )
    if current_score >= base + target:
        return f"already helps: {current_score - base:+.3f} over base at n={current_n}"
    if n_target is None:
        return f"target lift +{target:.3f} is unreachable (above the plateau)"
    return f"needs about {n_target / current_n:.1f}x more data to reach +{target:.3f} over base"


def evaluate(
    observations: list[TrainingObservation], base_score: float, target_lift: float = 0.05
) -> TuneResult:
    """Fit the curve and return an honest verdict on fine-tuning's value."""
    curve = fit_curve(observations)
    current_n = max(o.n_train for o in observations)
    current_score = curve.predict(current_n)
    n_target = curve.n_for(base_score + target_lift)
    multiple = (n_target / current_n) if n_target is not None else None
    return TuneResult(
        base_score=base_score,
        current_n=current_n,
        current_score=round(current_score, 4),
        target_lift=target_lift,
        n_for_target=n_target,
        data_multiple=multiple,
        verdict=_verdict(curve, base_score, current_score, target_lift, n_target, current_n),
    )
