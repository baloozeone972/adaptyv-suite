"""Tests for the Beta belief and the strict simulated oracle."""

from __future__ import annotations

import numpy as np
from binder_triage.schemas import Candidate
from dbtl_agent.belief import ClusterBelief
from dbtl_agent.oracle import SimulatedOracle


def test_belief_prior_and_update() -> None:
    b = ClusterBelief()
    assert b.mean(0) == 0.5  # uniform prior
    b.update(0, binders=8, total=10)
    assert b.mean(0) > 0.5  # shifted towards binding
    b.update(1, binders=1, total=10)
    assert b.mean(1) < 0.5


def test_thompson_in_unit_interval() -> None:
    b = ClusterBelief()
    rng = np.random.default_rng(0)
    samples = [b.thompson(0, rng) for _ in range(100)]
    assert all(0.0 <= s <= 1.0 for s in samples)


def test_oracle_is_strict_and_deterministic() -> None:
    cands = [
        Candidate(name="sure", sequence="A" * 60, p_bind_pred=1.0, cluster=0, p_bind_true=1.0),
        Candidate(name="never", sequence="K" * 60, p_bind_pred=0.0, cluster=1, p_bind_true=0.0),
    ]
    results = SimulatedOracle(seed=0).reveal(cands)
    assert set(results) == {"sure", "never"}  # only submitted designs revealed
    assert results["sure"] is True
    assert results["never"] is False
