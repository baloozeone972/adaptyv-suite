"""Shared statistics primitives.

The house style from Adaptyv's own posts: never a bare number. Everything here
returns an estimate with a bootstrap confidence interval so downstream tools
cannot accidentally report a point estimate alone.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class Estimate:
    """A point estimate with a percentile bootstrap confidence interval."""

    value: float
    ci_low: float
    ci_high: float
    n: int

    def as_tuple(self) -> tuple[float, float, float]:
        """Return (value, ci_low, ci_high)."""
        return (self.value, self.ci_low, self.ci_high)


def bootstrap_ci(
    data: Sequence[float] | NDArray[np.float64],
    statistic: Callable[[NDArray[np.float64]], float] = np.mean,
    n_resamples: int = 1000,
    ci: float = 95.0,
    seed: int = 0,
) -> Estimate:
    """Bootstrap a statistic over `data` by resampling with replacement.

    >>> est = bootstrap_ci([1.0, 1.0, 1.0, 1.0], n_resamples=50)
    >>> (est.value, est.ci_low, est.ci_high)
    (1.0, 1.0, 1.0)
    """
    arr = np.asarray(data, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("bootstrap_ci requires at least one observation")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_resamples, arr.size))
    resampled = np.array([statistic(arr[row]) for row in idx], dtype=np.float64)
    half = (100.0 - ci) / 2.0
    lo, hi = np.percentile(resampled, [half, 100.0 - half])
    return Estimate(
        value=float(statistic(arr)), ci_low=float(lo), ci_high=float(hi), n=int(arr.size)
    )
