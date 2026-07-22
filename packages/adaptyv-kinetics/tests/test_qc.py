"""QC detection: each injected artifact is caught, clean curves pass."""

from __future__ import annotations

import numpy as np
from adaptyv_core.schemas import Severity, Verdict
from adaptyv_kinetics.io.synthetic import ProteinSpec, _apply_artifacts, _clean_curve, _time_grid
from adaptyv_kinetics.qc.rules import evaluate
from adaptyv_kinetics.schemas import Trace

_CONC = [3.125, 6.25, 12.5, 25.0, 50.0]


def _traces(spec: ProteinSpec, seed: int) -> list[Trace]:
    rng = np.random.default_rng(seed)
    t = _time_grid()
    out: list[Trace] = []
    for c in _CONC:
        y = _apply_artifacts(t, _clean_curve(spec, c), spec, rng) + rng.normal(
            0, spec.noise, t.size
        )
        out.append(
            Trace(
                name=spec.name, replicate=1, concentration_nM=c, t=t.tolist(), y=y.round(3).tolist()
            )
        )
    return out


def _codes(spec: ProteinSpec) -> set[str]:
    return {f.code for f in evaluate(_traces(spec, seed=3), bootstrap=0).flags}


def test_clean_binder_passes() -> None:
    v = evaluate(_traces(ProteinSpec("b", kd_nM=13.2, kon=1e5, rmax=0.8), 0), bootstrap=0)
    assert v.verdict == Verdict.PASS
    assert v.flags == []


def test_non_binder_low_snr() -> None:
    assert "LOW_SNR" in _codes(ProteinSpec("b", non_binder=True))


def test_incomplete_dissociation() -> None:
    assert "INCOMPLETE_DISSOCIATION" in _codes(
        ProteinSpec("b", kd_nM=50.0, kon=1e5, artifacts=["incomplete_dissociation"])
    )


def test_spike() -> None:
    assert "SPIKE" in _codes(ProteinSpec("b", kd_nM=20.0, kon=1e5, artifacts=["spike"]))


def test_verdict_reject_on_critical() -> None:
    v = evaluate(_traces(ProteinSpec("b", non_binder=True), 0), bootstrap=0)
    assert v.verdict == Verdict.REJECT
    assert any(f.severity == Severity.CRITICAL for f in v.flags)


def test_baseline_drift_does_not_pass_clean() -> None:
    # Drift is not shipped as its own rule; it must still not slip through as PASS.
    spec = ProteinSpec("b", kd_nM=8.0, kon=1.5e5, rmax=0.6, artifacts=["baseline_drift"])
    v = evaluate(_traces(spec, seed=2), bootstrap=0)
    assert v.verdict != Verdict.PASS
