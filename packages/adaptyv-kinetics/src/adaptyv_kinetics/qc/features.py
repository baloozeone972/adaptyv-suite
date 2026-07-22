"""Curve-shape descriptors used by the QC rules.

Computed on the highest-concentration trace of a replicate, where signal is
strongest. Each descriptor is interpretable so a flag can always be explained,
and each is defined independently of the association/dissociation split so it
stays robust when that split is only inferred.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from adaptyv_kinetics.schemas import Trace


@dataclass(frozen=True, slots=True)
class Features:
    """Interpretable shape descriptors for one trace."""

    peak: float
    noise_std: float
    snr: float
    decay_fraction: float  # (peak - final) / (peak - baseline); ~0 means no dissociation
    max_spike_sigma: float  # largest |2nd difference| in units of its own sigma


def compute_features(trace: Trace) -> Features:
    """Compute shape descriptors for a single trace."""
    y = np.asarray(trace.y, dtype=np.float64)
    n = y.size

    baseline = float(np.min(y[: max(n // 10, 1)]))
    peak = float(np.max(y))
    tail = y[-max(n // 4, 2) :]
    noise_std = float(np.std(tail)) or 1e-9
    snr = (peak - baseline) / noise_std

    y_end = float(np.median(y[-max(n // 20, 1) :]))
    decay_fraction = (peak - y_end) / (peak - baseline + 1e-12)

    second = np.diff(y, n=2)
    spike_sigma = float(np.max(np.abs(second)) / (np.std(second) + 1e-12)) if second.size else 0.0

    return Features(peak, noise_std, snr, decay_fraction, spike_sigma)
