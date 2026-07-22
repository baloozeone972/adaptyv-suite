"""Tests for strategy evaluation, ranking and the crossover analysis."""

from __future__ import annotations

import pytest
from adaptyv_core import pricing
from adaptyv_core.schemas import AssayType
from campaign_planner.planner import STRATEGIES, evaluate, plan, two_step_crossover
from campaign_planner.schemas import Probs


def test_two_step_ranked_first_at_low_expression() -> None:
    results = plan(96, Probs(0.3, 0.15), budget=20000, sims=2000)
    assert results[0].name == "two_step_expression_then_affinity"
    assert results[0].within_budget


def test_direct_ranked_first_at_high_expression() -> None:
    results = plan(96, Probs(0.9, 0.15), budget=20000, sims=2000)
    assert results[0].name == "direct_affinity"


def test_over_budget_flagged_and_ranked_last() -> None:
    results = plan(96, Probs(0.9, 0.15), budget=18000, sims=1500)
    assert not results[-1].within_budget


def test_cost_per_binder_none_without_binders() -> None:
    r = evaluate("direct_affinity", STRATEGIES["direct_affinity"], 96, Probs(0.5, 0.0), 0.0, 500, 0)
    assert r.expected_binders == 0.0
    assert r.cost_per_binder is None


def test_crossover_is_a_probability() -> None:
    c = two_step_crossover(96)
    assert c is not None
    assert 0.0 < c < 1.0


def test_crossover_none_when_filter_never_pays(monkeypatch: pytest.MonkeyPatch) -> None:
    # Make expression as expensive as affinity: the filter can never pay for itself.
    monkeypatch.setitem(pricing.UNIT_PRICE_USD, AssayType.EXPRESSION, 169.0)
    assert two_step_crossover(96) is None


def test_as_row_renders() -> None:
    r = plan(96, Probs(0.4, 0.15), budget=20000, sims=500)[0]
    assert "binders" in r.as_row()
