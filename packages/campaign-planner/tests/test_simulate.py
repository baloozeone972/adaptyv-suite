"""Tests for the Monte-Carlo yield/cost simulation."""

from __future__ import annotations

from campaign_planner.schemas import Probs
from campaign_planner.simulate import simulate_direct, simulate_two_step


def test_direct_shapes_and_yield() -> None:
    binders, cost, duration = simulate_direct(96, Probs(0.5, 0.2), sims=4000, seed=0)
    assert binders.size == cost.size == 4000
    assert abs(binders.mean() - 96 * 0.5 * 0.2) < 1.0  # ~9.6 binders
    assert (cost == cost[0]).all()  # direct cost is deterministic
    assert duration == 21


def test_two_step_cheaper_at_low_expression() -> None:
    probs = Probs(0.3, 0.15)
    _, direct_cost, _ = simulate_direct(96, probs, sims=3000, seed=1)
    _, two_cost, two_dur = simulate_two_step(96, probs, sims=3000, seed=1)
    assert two_cost.mean() < direct_cost.mean()  # filtering first saves money here
    assert two_dur > 21  # but it is sequential, so slower


def test_two_step_same_expected_yield() -> None:
    probs = Probs(0.4, 0.2)
    d_binders, _, _ = simulate_direct(96, probs, sims=5000, seed=2)
    t_binders, _, _ = simulate_two_step(96, probs, sims=5000, seed=2)
    assert abs(d_binders.mean() - t_binders.mean()) < 1.0
