"""Edge cases: tiny inputs, single concentration, unknown export format, robustness."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from adaptyv_kinetics.models.fitting import fit_replicate
from adaptyv_kinetics.models.langmuir import NM_TO_M, infer_assoc_end, response
from adaptyv_kinetics.qc.features import compute_features
from adaptyv_kinetics.report.export import export_fits
from adaptyv_kinetics.schemas import Trace
from hypothesis import given, settings
from hypothesis import strategies as st

_T = np.arange(0.0, 180.0 + 480.0 + 4.0, 4.0)


def _trace(conc: float, kd_nM: float = 13.2) -> Trace:
    koff = kd_nM * NM_TO_M * 1e5
    y = response(_T, 1e5, koff, 0.8, conc * NM_TO_M, 180.0)
    return Trace(name="b", replicate=1, concentration_nM=conc, t=_T.tolist(), y=y.tolist())


def test_infer_assoc_end_small_array() -> None:
    assert infer_assoc_end(np.array([0.0, 1.0, 2.0]), np.array([0.0, 5.0, 1.0])) == 1.0


def test_single_concentration_fit_runs() -> None:
    fit = fit_replicate([_trace(50.0)], bootstrap=0)
    assert fit.converged
    assert fit.n_points == _T.size


def test_export_unknown_format_raises(tmp_path: Path) -> None:
    fit = fit_replicate([_trace(50.0)], bootstrap=0)
    with pytest.raises(ValueError):
        export_fits([fit], tmp_path / "x.xml", fmt="xml")


def test_features_on_flat_curve() -> None:
    flat = Trace(name="b", replicate=1, concentration_nM=10, t=_T.tolist(), y=[0.0] * _T.size)
    feat = compute_features(flat)
    assert feat.snr >= 0.0  # no division error on zero-variance input


@settings(max_examples=25, deadline=None)
@given(
    kd=st.floats(min_value=1.0, max_value=200.0),
    noise=st.floats(min_value=0.0, max_value=0.03),
    seed=st.integers(min_value=0, max_value=50),
)
def test_fit_never_crashes_and_stays_finite(kd: float, noise: float, seed: int) -> None:
    rng = np.random.default_rng(seed)
    koff = kd * NM_TO_M * 1e5
    traces = []
    for c in (6.25, 25.0, 50.0):
        y = response(_T, 1e5, koff, 0.8, c * NM_TO_M, 180.0) + rng.normal(0, noise, _T.size)
        traces.append(Trace(name="b", replicate=1, concentration_nM=c, t=_T.tolist(), y=y.tolist()))
    fit = fit_replicate(traces, bootstrap=0)
    assert np.isfinite(fit.kd_M)
    assert fit.kon > 0 and fit.koff > 0
