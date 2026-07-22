"""Monte-Carlo yield and cost for each strategy.

Two-step is sequential, so its cost is stochastic (the affinity plate tier depends
on how many designs survive expression) and its duration is the sum of both stages.
That stochastic cost is exactly why a simulation — not a point estimate — is right.
"""

from __future__ import annotations

import numpy as np
from adaptyv_core.pricing import price
from adaptyv_core.schemas import AssayType
from numpy.typing import NDArray

from campaign_planner.schemas import Probs

Array = NDArray[np.float64]


def simulate_direct(n: int, probs: Probs, sims: int, seed: int) -> tuple[Array, Array, int]:
    """Run affinity on all n designs; non-expressers simply fail."""
    rng = np.random.default_rng(seed)
    binders = rng.binomial(n, probs.p_express * probs.p_bind, sims).astype(np.float64)
    cost = price(AssayType.AFFINITY, n)
    return binders, np.full(sims, cost.total_usd), cost.duration_days


def simulate_two_step(n: int, probs: Probs, sims: int, seed: int) -> tuple[Array, Array, int]:
    """Cheap expression filter first, then affinity only on the survivors."""
    rng = np.random.default_rng(seed)
    expressed = rng.binomial(n, probs.p_express, sims)
    binders = rng.binomial(expressed, probs.p_bind).astype(np.float64)
    expr = price(AssayType.EXPRESSION, n)
    tier_cost = {
        e: (price(AssayType.AFFINITY, int(e)).total_usd if e else 0.0) for e in np.unique(expressed)
    }
    cost_affinity = np.array([tier_cost[e] for e in expressed], dtype=np.float64)
    duration = expr.duration_days + price(AssayType.AFFINITY, n).duration_days
    return binders, expr.total_usd + cost_affinity, duration
