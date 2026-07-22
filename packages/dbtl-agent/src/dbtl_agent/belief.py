"""Per-family Beta belief with Thompson sampling for explore/exploit.

Each design family gets a Beta(alpha, beta) posterior over its binding rate, updated
from observed outcomes. Thompson sampling — score a candidate by a *sample* from its
family's posterior — explores wide early (uncertain families) and exploits later
(confident ones), without a hand-tuned schedule.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class ClusterBelief:
    """Beta posteriors keyed by family id. Uniform Beta(1, 1) prior."""

    alpha: dict[int, float] = field(default_factory=dict)
    beta: dict[int, float] = field(default_factory=dict)

    def update(self, cluster: int, binders: int, total: int) -> None:
        """Fold in `binders` successes out of `total` trials for a family."""
        self.alpha[cluster] = self.alpha.get(cluster, 1.0) + binders
        self.beta[cluster] = self.beta.get(cluster, 1.0) + (total - binders)

    def thompson(self, cluster: int, rng: np.random.Generator) -> float:
        """Sample a plausible binding rate for a family (exploration built in)."""
        return float(rng.beta(self.alpha.get(cluster, 1.0), self.beta.get(cluster, 1.0)))

    def mean(self, cluster: int) -> float:
        """Posterior mean binding rate for a family."""
        a = self.alpha.get(cluster, 1.0)
        b = self.beta.get(cluster, 1.0)
        return a / (a + b)
