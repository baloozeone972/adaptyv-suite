"""Calibrate Mosaic's predicted objective terms against Adaptyv's measurements."""

from __future__ import annotations

import numpy as np

from mosaic_loop.schemas import Calibration, DesignMeasurement, DriftReport, ObjectiveTerm
from mosaic_loop.stats import pearson, spearman

DEFAULT_WEIGHTS: dict[ObjectiveTerm, float] = {
    ObjectiveTerm.AFFINITY: 0.5,
    ObjectiveTerm.SOLUBILITY: 0.3,
    ObjectiveTerm.STABILITY: 0.2,
}


def _pair(
    measurements: list[DesignMeasurement], term: ObjectiveTerm
) -> tuple[np.ndarray, np.ndarray]:
    rows = [m for m in measurements if term in m.predicted and term in m.measured]
    p = np.array([m.predicted[term] for m in rows], dtype=np.float64)
    y = np.array([m.measured[term] for m in rows], dtype=np.float64)
    return p, y


def calibrate_term(measurements: list[DesignMeasurement], term: ObjectiveTerm) -> Calibration:
    """Fit measured ≈ slope·predicted + intercept and report how well it tracks reality."""
    p, y = _pair(measurements, term)
    slope, intercept = (
        np.polyfit(p, y, 1)
        if len(p) >= 2 and p.std() > 0
        else (0.0, float(y.mean()) if len(y) else 0.0)
    )
    calibrated = slope * p + intercept
    mae = float(np.mean(np.abs(y - calibrated))) if len(y) else 0.0
    return Calibration(
        term=term,
        n=len(p),
        slope=float(slope),
        intercept=float(intercept),
        pearson=pearson(p, y),
        spearman=spearman(p, y),
        mae_after=mae,
    )


def _composite(
    measurements: list[DesignMeasurement],
    weights: dict[ObjectiveTerm, float],
    use: str,
    cals: dict[ObjectiveTerm, Calibration],
) -> np.ndarray:
    scores = []
    for m in measurements:
        total = 0.0
        for term, w in weights.items():
            if use == "measured":
                total += w * m.measured.get(term, 0.0)
            elif use == "calibrated" and term in cals:
                total += w * (cals[term].slope * m.predicted.get(term, 0.0) + cals[term].intercept)
            else:
                total += w * m.predicted.get(term, 0.0)
        scores.append(total)
    return np.array(scores, dtype=np.float64)


def analyze(
    measurements: list[DesignMeasurement], weights: dict[ObjectiveTerm, float] | None = None
) -> DriftReport:
    """Calibrate every term and measure how much recalibration aligns the objective."""
    weights = weights or DEFAULT_WEIGHTS
    cals = {term: calibrate_term(measurements, term) for term in weights}
    measured = _composite(measurements, weights, "measured", cals)
    raw = _composite(measurements, weights, "predicted", cals)
    calibrated = _composite(measurements, weights, "calibrated", cals)
    return DriftReport(
        calibrations=list(cals.values()),
        objective_agreement_raw=spearman(raw, measured),
        objective_agreement_calibrated=spearman(calibrated, measured),
        weights=weights,
    )
