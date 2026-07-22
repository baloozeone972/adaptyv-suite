"""Fitter validation: parameter recovery and noise robustness."""

from __future__ import annotations

import numpy as np
import pytest
from adaptyv_kinetics.models.fitting import fit_replicate
from adaptyv_kinetics.models.langmuir import NM_TO_M, response
from adaptyv_kinetics.schemas import Trace

_CONC = [3.125, 6.25, 12.5, 25.0, 50.0]
_T = np.arange(0.0, 180.0 + 480.0 + 4.0, 4.0)


def _traces(
    kd_nM: float, kon: float, rmax: float, noise: float, seed: int, rounded: bool = True
) -> list[Trace]:
    rng = np.random.default_rng(seed)
    koff = kd_nM * NM_TO_M * kon
    out: list[Trace] = []
    for c in _CONC:
        y = response(_T, kon, koff, rmax, c * NM_TO_M, 180.0) + rng.normal(0, noise, _T.size)
        if rounded:
            y = y.round(3)
        out.append(Trace(name="b", replicate=1, concentration_nM=c, t=_T.tolist(), y=y.tolist()))
    return out


def test_exact_recovery_within_1_percent() -> None:
    # Exact model data (no noise, no 3-decimal rounding): the fitter must be correct.
    fit = fit_replicate(_traces(13.2, 1e5, 0.8, noise=0.0, seed=0, rounded=False), bootstrap=0)
    assert abs(fit.kd_M * 1e9 - 13.2) / 13.2 < 0.01
    assert fit.converged


def test_noise_robustness_median_error() -> None:
    errs = [
        abs(fit_replicate(_traces(13.2, 1e5, 0.8, 0.01, s), bootstrap=0).kd_M * 1e9 - 13.2)
        for s in range(6)
    ]
    assert np.median(errs) / 13.2 < 0.15


def test_bootstrap_ci_brackets_estimate() -> None:
    fit = fit_replicate(_traces(13.2, 1e5, 0.8, 0.01, seed=1), bootstrap=100)
    lo, hi = fit.kd_ci95
    assert lo <= fit.kd_M <= hi


def test_empty_raises() -> None:
    with pytest.raises(ValueError):
        fit_replicate([], bootstrap=0)
