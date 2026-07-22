"""A strict simulated lab.

Strict means it only ever reveals outcomes for designs that exist in the pool
(their generated `p_bind_true`). Nothing is invented — that is what makes the
backtest honest. On real runs this is replaced by the Foundry, gated by the guard.
"""

from __future__ import annotations

import numpy as np
from binder_triage.schemas import Candidate


class SimulatedOracle:
    """Reveals binding outcomes by a Bernoulli draw on each design's true probability."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = np.random.default_rng(seed)

    def reveal(self, candidates: list[Candidate]) -> dict[str, bool]:
        """Return {name: bound?} for the submitted candidates only."""
        return {c.name: bool(self._rng.random() < (c.p_bind_true or 0.0)) for c in candidates}
