"""Tests for the guardrail proxy, against a real-shaped fake transport."""

from __future__ import annotations

import pytest
from adaptyv_core.foundry import AssayRequest, FoundryClient
from adaptyv_core.guard import Budget, Guard, Policy
from adaptyv_core.schemas import AssayType
from foundry_guard.proxy import GuardedLab


class FakeTransport:
    """$169/sequence; `fail_submit` makes the create call raise."""

    def __init__(self, fail_submit: bool = False) -> None:
        self.fail_submit = fail_submit
        self._status: dict[str, str] = {}

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            spec = payload["experiment_spec"]  # type: ignore[index]
            n = len(spec["sequences"])  # type: ignore[index, arg-type]
            return {"breakdown": {"total_cents": 169_00 * n}}
        if path == "/experiments":
            if self.fail_submit:
                raise RuntimeError("upstream failure")
            exp_id = "exp-1"
            self._status[exp_id] = "waiting_for_materials"
            return {"experiment_id": exp_id}
        return {}  # pragma: no cover

    def get(self, path: str, token: str) -> dict[str, object]:
        exp_id = path.rsplit("/", 1)[-1]
        return {"id": exp_id, "status": self._status.get(exp_id, "draft")}

    def get_bytes(self, path: str, token: str) -> bytes:  # pragma: no cover
        return b""

    def fetch_url(self, url: str) -> bytes:  # pragma: no cover
        return b""


def _request(assay: AssayType, n: int) -> AssayRequest:
    return AssayRequest(experiment_type=assay, sequences={f"d{i}": "A" * 60 for i in range(n)})


def _lab(budget: float = 5000.0, fail_submit: bool = False, approval=None):  # type: ignore[no-untyped-def]
    policy = Policy(
        max_total_usd=budget,
        max_per_call_usd=2000.0,
        allowed_assays={AssayType.AFFINITY},
        require_approval_over_usd=1500.0,
    )
    guard = Guard(policy=policy, budget=Budget(budget))
    client = FoundryClient(FakeTransport(fail_submit=fail_submit), "tok")
    lab = GuardedLab(client, guard) if approval is None else GuardedLab(client, guard, approval)
    return lab, guard


def test_allowed_submission_commits_and_audits() -> None:
    lab, guard = _lab()
    result = lab.submit(_request(AssayType.AFFINITY, 5), name="small affinity")
    assert result.allowed
    assert result.experiment_id == "exp-1"
    assert guard.budget.spent == 845.0
    assert guard.journal.verify()
    assert any(e.event == "submitted" for e in guard.journal.entries())


def test_out_of_scope_denied_without_spending() -> None:
    lab, guard = _lab()
    result = lab.submit(_request(AssayType.EXPRESSION, 5), name="x")
    assert not result.allowed
    assert guard.budget.spent == 0.0


def test_over_per_call_cap_denied() -> None:
    lab, guard = _lab()
    assert not lab.submit(_request(AssayType.AFFINITY, 20), name="x").allowed  # 20*169 > 2000
    assert guard.budget.spent == 0.0


def test_budget_denied() -> None:
    lab, guard = _lab(budget=500.0)
    assert not lab.submit(_request(AssayType.AFFINITY, 5), name="x").allowed  # 845 > 500
    assert guard.budget.spent == 0.0


def test_approval_required_default_denies() -> None:
    lab, _guard = _lab()
    result = lab.submit(_request(AssayType.AFFINITY, 10), name="x")  # 1690 > approval threshold
    assert not result.allowed
    assert "approval" in result.reason


def test_approval_granted_allows() -> None:
    lab, _guard = _lab(approval=lambda request, amount: True)
    assert lab.submit(_request(AssayType.AFFINITY, 10), name="x").allowed


def test_submit_failure_releases_budget() -> None:
    lab, guard = _lab(fail_submit=True)
    with pytest.raises(RuntimeError):
        lab.submit(_request(AssayType.AFFINITY, 5), name="x")
    assert guard.budget.spent == 0.0
    assert guard.budget.available == 5000.0  # reservation released
    assert any(e.event == "submit_failed" for e in guard.journal.entries())


def test_sequence_never_exceeds_budget() -> None:
    lab, guard = _lab(budget=2000.0)  # per-call cap 2000; each 5-design call is 845
    results = [lab.submit(_request(AssayType.AFFINITY, 5), name="x") for _ in range(5)]
    assert sum(r.allowed for r in results) == 2  # only two fit; the rest denied
    assert guard.budget.spent <= 2000.0
