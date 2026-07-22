"""Feature extraction for triage.

Builds on adaptyv-kinetics: per-replicate fit quality and curve shape, plus a
protein-level consistency feature (how far the K_D disagrees across replicates).
Consistency is exactly what a per-replicate QC pass (spec G) cannot see.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from adaptyv_kinetics.models.fitting import fit_replicate
from adaptyv_kinetics.qc.features import compute_features
from adaptyv_kinetics.schemas import Trace

from sensorgram_triage.schemas import FEATURE_NAMES


@dataclass(frozen=True, slots=True)
class FeatureRow:
    """A feature vector for one replicate, keyed by (name, replicate)."""

    name: str
    replicate: int
    vector: np.ndarray  # ordered as schemas.FEATURE_NAMES


def _group(traces: list[Trace]) -> dict[tuple[str, int], list[Trace]]:
    groups: dict[tuple[str, int], list[Trace]] = defaultdict(list)
    for tr in traces:
        if not tr.is_control:
            groups[(tr.name, tr.replicate)].append(tr)
    return groups


def _kd_log_spread(kds_by_name: dict[str, list[float]]) -> dict[str, float]:
    spread: dict[str, float] = {}
    for name, kds in kds_by_name.items():
        logs = [math.log10(k) for k in kds if k > 0]
        spread[name] = (max(logs) - min(logs)) if len(logs) > 1 else 0.0
    return spread


def extract(traces: list[Trace]) -> list[FeatureRow]:
    """Extract one feature vector per replicate from a package's traces."""
    groups = _group(traces)
    fits = {key: fit_replicate(group, bootstrap=0) for key, group in groups.items()}
    kds_by_name: dict[str, list[float]] = defaultdict(list)
    for (name, _), fit in fits.items():
        kds_by_name[name].append(fit.kd_M)
    spread = _kd_log_spread(kds_by_name)

    rows: list[FeatureRow] = []
    for (name, replicate), group in groups.items():
        fit = fits[(name, replicate)]
        strongest = max(group, key=lambda tr: float(np.max(tr.y)))
        feat = compute_features(strongest)
        vector = np.array(
            [
                feat.snr,
                fit.rel_mae,
                feat.decay_fraction,
                feat.max_spike_sigma,
                float(fit.converged),
                spread[name],
            ],
            dtype=np.float64,
        )
        assert vector.size == len(FEATURE_NAMES)
        rows.append(FeatureRow(name=name, replicate=replicate, vector=vector))
    return rows
