"""Tests for the DBTL loop: the guarantees and the learning lift."""

from __future__ import annotations

import numpy as np
from adaptyv_core.guard import Policy
from adaptyv_core.pricing import price
from adaptyv_core.schemas import AssayType
from binder_triage.pool import synthetic_pool
from dbtl_agent.loop import random_baseline, run_campaign


def _policy(budget: float, batch: int = 12) -> Policy:
    return Policy(
        max_total_usd=budget,
        max_per_call_usd=price(AssayType.AFFINITY, batch).total_usd,
        allowed_assays={AssayType.AFFINITY},
    )


def test_budget_is_never_exceeded_and_audited() -> None:
    pool = synthetic_pool(n_clusters=4, per_cluster=20, seed=0)
    out = run_campaign(pool, _policy(9000), batch_size=12, max_rounds=10, seed=0)
    assert out.budget_respected
    assert out.total_cost_usd <= 9000
    assert out.audit_valid


def test_tight_budget_stops_early() -> None:
    pool = synthetic_pool(n_clusters=4, per_cluster=20, seed=0)
    one_round = price(AssayType.AFFINITY, 12).total_usd
    out = run_campaign(pool, _policy(one_round + 1, batch=12), batch_size=12, max_rounds=10, seed=0)
    assert len(out.rounds) == 1  # only one round fits


def test_pool_not_retested() -> None:
    pool = synthetic_pool(n_clusters=4, per_cluster=20, seed=0)
    out = run_campaign(pool, _policy(100_000), batch_size=12, max_rounds=10, seed=0)
    assert out.total_submitted <= len(pool)  # never tests more than exist


def test_agent_beats_random_on_average() -> None:
    agent, random = [], []
    for seed in range(6):
        pool = synthetic_pool(n_clusters=6, per_cluster=24, seed=seed)
        out = run_campaign(
            pool,
            _policy(40_000, batch=24),
            batch_size=24,
            max_rounds=4,
            diversity_weight=0.3,
            seed=seed,
        )
        agent.append(out.total_binders)
        random.append(random_baseline(pool, batch_size=24, max_rounds=len(out.rounds), seed=seed))
    assert np.mean(agent) > np.mean(random)  # learning helps


def test_diversity_avoids_monoculture() -> None:
    pool = synthetic_pool(n_clusters=6, per_cluster=40, seed=0)
    out = run_campaign(
        pool, _policy(40_000, batch=24), batch_size=24, max_rounds=3, diversity_weight=0.5, seed=0
    )
    assert all(r.n_families >= 3 for r in out.rounds)  # never collapses to one family


def test_cumulative_hit_rate() -> None:
    pool = synthetic_pool(n_clusters=4, per_cluster=20, seed=0)
    out = run_campaign(pool, _policy(20_000), batch_size=12, max_rounds=3, seed=0)
    assert 0.0 <= out.cumulative_hit_rate <= 1.0


def test_random_baseline_stops_when_pool_exhausted() -> None:
    pool = synthetic_pool(n_clusters=1, per_cluster=30, seed=0)  # 30 designs
    total = random_baseline(pool, batch_size=24, max_rounds=5, seed=0)  # only 1 full batch fits
    assert 0 <= total <= 24
