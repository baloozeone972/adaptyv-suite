"""Tests for budget guardrails and the hash-chained audit journal."""

from __future__ import annotations

import dataclasses

from adaptyv_core.guard import AuditJournal, Budget, Guard, Policy
from adaptyv_core.schemas import AssayType
from hypothesis import given, settings
from hypothesis import strategies as st


def test_reserve_commit_release() -> None:
    b = Budget(max_total_usd=1000.0)
    rid = b.reserve(400.0)
    assert rid is not None
    assert b.available == 600.0
    b.commit(rid)
    assert b.spent == 400.0
    assert b.available == 600.0
    rid2 = b.reserve(600.0)
    assert rid2 is not None
    b.release(rid2)
    assert b.available == 600.0


def test_reserve_refused_over_budget() -> None:
    b = Budget(max_total_usd=100.0)
    assert b.reserve(150.0) is None
    assert b.reserve(-5.0) is None


def test_audit_chain_verifies_and_detects_tampering() -> None:
    j = AuditJournal()
    j.append("a", {"x": 1})
    j.append("b", {"y": 2})
    assert j.verify()
    # Tamper with the first entry's data but keep its old hash.
    j._entries[0] = dataclasses.replace(j._entries[0], data={"x": 999})
    assert not j.verify()


def test_audit_detects_broken_chain_link() -> None:
    j = AuditJournal()
    j.append("a", {"x": 1})
    j.append("b", {"y": 2})
    # Break the chain link: second entry no longer points at the first entry's hash.
    j._entries[1] = dataclasses.replace(j._entries[1], prev_hash="genesis")
    assert not j.verify()


def _policy(total: float = 10_000.0) -> Policy:
    return Policy(
        max_total_usd=total,
        max_per_call_usd=5_000.0,
        allowed_assays={AssayType.AFFINITY},
        require_approval_over_usd=3_000.0,
    )


def test_guard_scope_denies_unlisted_assay() -> None:
    g = Guard(policy=_policy(), budget=Budget(10_000.0))
    assert not g.authorize(AssayType.EXPRESSION, 100.0).allowed


def test_guard_per_call_cap() -> None:
    g = Guard(policy=_policy(), budget=Budget(10_000.0))
    assert not g.authorize(AssayType.AFFINITY, 6_000.0).allowed


def test_guard_budget_cap() -> None:
    g = Guard(policy=_policy(total=1_000.0), budget=Budget(1_000.0))
    assert not g.authorize(AssayType.AFFINITY, 2_000.0).allowed


def test_guard_approval_threshold() -> None:
    g = Guard(policy=_policy(), budget=Budget(10_000.0))
    d = g.authorize(AssayType.AFFINITY, 4_000.0)
    assert d.allowed and d.needs_approval


def test_guard_records_every_decision() -> None:
    g = Guard(policy=_policy(), budget=Budget(10_000.0))
    g.authorize(AssayType.AFFINITY, 100.0)
    g.authorize(AssayType.EXPRESSION, 100.0)
    assert len(g.journal.entries()) == 2
    assert g.journal.verify()


@settings(max_examples=60)
@given(amounts=st.lists(st.floats(min_value=0.0, max_value=500.0), min_size=0, max_size=40))
def test_property_budget_never_exceeded(amounts: list[float]) -> None:
    b = Budget(max_total_usd=1_000.0)
    for amount in amounts:
        rid = b.reserve(amount)
        if rid is not None and int(amount) % 2 == 0:
            b.commit(rid)
        elif rid is not None:
            b.release(rid)
        assert b.available >= -1e-9  # never over-committed
        assert b.spent + sum(b._reserved.values()) <= b.max_total_usd + 1e-9
