"""Evaluate and rank strategies; find the two-step crossover point."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from adaptyv_core.pricing import price
from adaptyv_core.schemas import AssayType
from numpy.typing import NDArray

from campaign_planner.schemas import Probs, StrategyResult
from campaign_planner.simulate import simulate_direct, simulate_two_step

Array = NDArray[np.float64]
_SimFn = Callable[[int, Probs, int, int], tuple[Array, Array, int]]

STRATEGIES: dict[str, _SimFn] = {
    "direct_affinity": simulate_direct,
    "two_step_expression_then_affinity": simulate_two_step,
}


def _ci(values: Array) -> tuple[float, float]:
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(lo), float(hi)


def evaluate(
    name: str, fn: _SimFn, n: int, probs: Probs, budget: float, sims: int, seed: int
) -> StrategyResult:
    """Simulate one strategy and summarise cost, yield and budget fit."""
    binders, cost, duration = fn(n, probs, sims, seed)
    mean_cost = float(cost.mean())
    mean_binders = float(binders.mean())
    return StrategyResult(
        name=name,
        n_input=n,
        total_cost_usd=round(mean_cost, 2),
        cost_ci95=_ci(cost),
        duration_days=duration,
        expected_binders=round(mean_binders, 2),
        binders_ci95=_ci(binders),
        within_budget=(budget <= 0 or mean_cost <= budget),
        cost_per_binder=round(mean_cost / mean_binders, 2) if mean_binders > 0 else None,
    )


def plan(
    n: int, probs: Probs, budget: float = 0.0, sims: int = 2000, seed: int = 0
) -> list[StrategyResult]:
    """Evaluate every strategy and rank: within-budget first, then most binders."""
    results = [evaluate(name, fn, n, probs, budget, sims, seed) for name, fn in STRATEGIES.items()]
    # Rank: within-budget first, then most binders, then cheaper (the tiebreaker that
    # makes the two-step win when it matches yield at lower cost).
    return sorted(
        results,
        key=lambda r: (not r.within_budget, -round(r.expected_binders), r.total_cost_usd),
    )


def two_step_crossover(n: int, grid: int = 199) -> float | None:
    """Highest P(express) at which the two-step is still cheaper than direct affinity.

    Above this expression rate, filtering first no longer pays for its overhead.
    Returns None if the two-step is never cheaper.
    """
    direct = price(AssayType.AFFINITY, n).total_usd
    expr = price(AssayType.EXPRESSION, n).total_usd
    best: float | None = None
    for i in range(1, grid + 1):
        p = i / (grid + 1)
        two_step = expr + price(AssayType.AFFINITY, round(n * p)).total_usd
        if two_step < direct:
            best = p
    return best
