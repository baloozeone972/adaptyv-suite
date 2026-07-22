"""Synthetic Mosaic export + Adaptyv measurements (declared synthetic).

Built so the three terms differ in how well Mosaic's prediction tracks reality:
affinity tracks well, solubility moderately, and stability is a poor proxy (the
predicted term is driven by a different latent factor than the measurement) — the
kind of honest, varied result the loop is meant to surface.
"""

from __future__ import annotations

import numpy as np

from mosaic_loop.schemas import DesignMeasurement, ObjectiveTerm


def synthetic_measurements(n: int = 120, seed: int = 0) -> list[DesignMeasurement]:
    """Generate paired (predicted, measured) objective terms for n designs."""
    rng = np.random.default_rng(seed)
    out: list[DesignMeasurement] = []
    for i in range(n):
        q_aff = float(rng.normal())
        q_sol = float(rng.normal())
        q_sta = float(rng.normal())
        q_confounder = float(rng.normal())  # what stability actually depends on
        predicted = {
            ObjectiveTerm.AFFINITY: 0.6 + 0.18 * q_aff + float(rng.normal(0, 0.04)),
            ObjectiveTerm.SOLUBILITY: 0.5 + 0.12 * q_sol + float(rng.normal(0, 0.13)),
            ObjectiveTerm.STABILITY: 0.5 + 0.15 * q_sta + float(rng.normal(0, 0.05)),
        }
        measured = {
            ObjectiveTerm.AFFINITY: 7.0 + 1.8 * q_aff + float(rng.normal(0, 0.25)),
            ObjectiveTerm.SOLUBILITY: 40.0 + 12.0 * q_sol + float(rng.normal(0, 10.0)),
            # stability is driven by a confounder Mosaic never saw -> poor proxy (drift)
            ObjectiveTerm.STABILITY: 55.0 + 8.0 * q_confounder + float(rng.normal(0, 3.0)),
        }
        out.append(
            DesignMeasurement(name=f"design_{i:03d}", predicted=predicted, measured=measured)
        )
    return out
