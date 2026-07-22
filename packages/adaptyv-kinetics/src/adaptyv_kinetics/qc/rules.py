"""Interpretable QC rule catalog.

Thresholds are named constants here (a YAML override is a planned extension).
Each rule maps a measured descriptor to a flag; the verdict follows the shared
convention: reject on any critical, review on any warning, else pass.
"""

from __future__ import annotations

import numpy as np
from adaptyv_core.schemas import Severity, Verdict

from adaptyv_kinetics.models.fitting import fit_replicate
from adaptyv_kinetics.qc.features import Features, compute_features
from adaptyv_kinetics.schemas import KineticFit, QCFlag, Trace, TraceVerdict

SNR_MIN = 10.0
DECAY_MIN = 0.10  # <10% dissociation → k_off not identifiable (per Adaptyv's guidance)
SPIKE_SIGMA_MAX = 6.0
POOR_FIT_REL_MAE = 0.15


def _flags(feat: Features, fit: KineticFit) -> list[QCFlag]:
    flags: list[QCFlag] = []
    if feat.snr < SNR_MIN:
        flags.append(
            QCFlag(
                code="LOW_SNR",
                severity=Severity.CRITICAL,
                message="Signal below the minimum usable signal-to-noise ratio",
                evidence={"snr": feat.snr},
            )
        )
    if feat.decay_fraction < DECAY_MIN:
        flags.append(
            QCFlag(
                code="INCOMPLETE_DISSOCIATION",
                severity=Severity.CRITICAL,
                message="Under 10% dissociation; k_off not identifiable",
                evidence={"decay_fraction": feat.decay_fraction},
            )
        )
    if feat.max_spike_sigma > SPIKE_SIGMA_MAX:
        flags.append(
            QCFlag(
                code="SPIKE",
                severity=Severity.WARNING,
                message="Aberrant point (2nd-derivative outlier)",
                evidence={"sigma": feat.max_spike_sigma},
            )
        )
    if fit.rel_mae > POOR_FIT_REL_MAE:
        flags.append(
            QCFlag(
                code="POOR_FIT",
                severity=Severity.WARNING,
                message="Fit rel_MAE above threshold",
                evidence={"rel_mae": fit.rel_mae},
            )
        )
    return flags


def _verdict(flags: list[QCFlag]) -> Verdict:
    severities = {f.severity for f in flags}
    if Severity.CRITICAL in severities:
        return Verdict.REJECT
    if Severity.WARNING in severities:
        return Verdict.REVIEW
    return Verdict.PASS


def evaluate(traces: list[Trace], bootstrap: int = 200) -> TraceVerdict:
    """Fit, extract features, apply rules, and return a verdict for one replicate."""
    fit = fit_replicate(traces, bootstrap=bootstrap)
    strongest = max(traces, key=lambda tr: np.max(tr.y))
    feat = compute_features(strongest)
    flags = _flags(feat, fit)
    return TraceVerdict(
        name=traces[0].name,
        replicate=traces[0].replicate,
        verdict=_verdict(flags),
        flags=flags,
        fit=fit,
    )
