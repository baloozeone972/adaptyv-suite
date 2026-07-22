"""Synthetic training-size sweep (declared synthetic).

Stands in for the real experiment that cannot run here: fine-tuning Boltz-2's affinity
head on increasing amounts of Adaptyv data and scoring it with grouped, leakage-free
splits. The generated curve has a plateau only modestly above the base model — the
honest, expected shape at a small data volume with a protein-protein domain shift.
"""

from __future__ import annotations

import numpy as np

from boltz_tune.schemas import TrainingObservation

# The (hidden) truth the harness has to recover from noisy points.
_TRUE_PLATEAU = 0.72
_TRUE_COEF = 0.9
_TRUE_ALPHA = 0.5
BASE_SCORE = 0.66  # the generic Boltz-2 affinity head, no fine-tuning


def synthetic_sweep(
    sizes: tuple[int, ...] = (50, 100, 200, 400, 800, 1600), seed: int = 0
) -> list[TrainingObservation]:
    """Measured model score at each training size, with realistic noise."""
    rng = np.random.default_rng(seed)
    out: list[TrainingObservation] = []
    for n in sizes:
        true = _TRUE_PLATEAU - _TRUE_COEF * n ** (-_TRUE_ALPHA)
        out.append(TrainingObservation(n_train=n, score=float(true + rng.normal(0, 0.01))))
    return out
