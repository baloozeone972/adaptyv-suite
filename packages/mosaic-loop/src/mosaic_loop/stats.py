"""Small correlation helpers (numpy, no external stats dependency)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def _rankdata(a: Array) -> Array:
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(1, len(a) + 1, dtype=np.float64)
    return ranks


def pearson(a: Array, b: Array) -> float:
    """Pearson correlation, 0.0 for degenerate input."""
    if len(a) < 2 or a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: Array, b: Array) -> float:
    """Spearman rank correlation."""
    if len(a) < 2:
        return 0.0
    return pearson(_rankdata(a), _rankdata(b))
