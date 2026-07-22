"""Tests for the pool, selection strategies and evaluation."""

from __future__ import annotations

from binder_triage.evaluate import compare, evaluate
from binder_triage.pool import synthetic_pool
from binder_triage.schemas import Candidate
from binder_triage.select import diverse_greedy, top_n


def test_pool_structure() -> None:
    pool = synthetic_pool(n_clusters=3, per_cluster=10, seed=0)
    assert len(pool) == 30
    assert {c.cluster for c in pool} == {0, 1, 2}
    assert all(0.0 <= c.p_bind_pred <= 1.0 for c in pool)


def test_top_n_maximises_predicted() -> None:
    pool = synthetic_pool(seed=0)
    chosen = top_n(pool, 24)
    assert len(chosen) == 24
    # every chosen candidate scores at least as high as any unchosen one
    threshold = min(c.p_bind_pred for c in chosen)
    assert all(c.p_bind_pred <= threshold for c in pool if c not in chosen)


def test_diverse_greedy_size_and_pure_topn_when_weight_zero() -> None:
    pool = synthetic_pool(seed=0)
    assert len(diverse_greedy(pool, 24, diversity_weight=0.0)) == 24
    # with zero diversity weight, greedy reduces to top-N predicted totals
    greedy0 = sum(c.p_bind_pred for c in diverse_greedy(pool, 24, 0.0))
    topn = sum(c.p_bind_pred for c in top_n(pool, 24))
    assert abs(greedy0 - topn) < 1e-9


def test_diversity_reduces_monoculture() -> None:
    pool = synthetic_pool(seed=0)
    top, div = compare(pool, 24, diversity_weight=0.8)
    assert top.expected_binders >= div.expected_binders  # top-N maximises predicted
    assert div.mean_pairwise_identity < top.mean_pairwise_identity  # less monoculture
    assert div.n_clusters > top.n_clusters  # more design families


def test_evaluate_fields() -> None:
    pool = synthetic_pool(n_clusters=3, per_cluster=10, seed=1)
    sel = evaluate("top_n", top_n(pool, 24))
    assert sel.plate_tier == 24
    assert sel.true_binders is not None  # synthetic ground truth present


def test_true_binders_none_without_ground_truth() -> None:
    cands = [Candidate(name="a", sequence="AAAA", p_bind_pred=0.5, cluster=0)]
    sel = evaluate("top_n", cands)
    assert sel.true_binders is None
