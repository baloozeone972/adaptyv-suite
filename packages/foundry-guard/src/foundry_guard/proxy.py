"""The guardrail proxy: enforce policy on every Foundry call the agent makes.

The agent does not have to cooperate. Every submission goes through: cost estimate
→ authorize (scope + per-call + budget) → human escalation if required → reserve →
submit → commit → audit. Any failure is default-deny and the budget is never
touched. Spending is reservation-based, so no call sequence can exceed the cap.
"""

from __future__ import annotations

from typing import Protocol

from adaptyv_core.foundry import AssayRequest, FoundryClient
from adaptyv_core.guard import Guard
from pydantic import BaseModel


class ApprovalGate(Protocol):
    """Called when a request exceeds the approval threshold. Returns True to allow."""

    def __call__(self, request: AssayRequest, amount_usd: float) -> bool: ...


def auto_deny(request: AssayRequest, amount_usd: float) -> bool:
    """Default escalation handler: deny until a human explicitly approves."""
    return False


class GuardedResult(BaseModel):
    """The outcome of a guarded submission."""

    allowed: bool
    reason: str
    amount_usd: float
    experiment_id: str | None = None


class GuardedLab:
    """Wrap a FoundryClient so every submission is policed by a Guard."""

    def __init__(
        self, client: FoundryClient, guard: Guard, approval: ApprovalGate = auto_deny
    ) -> None:
        self._client = client
        self._guard = guard
        self._approval = approval

    def submit(self, request: AssayRequest) -> GuardedResult:
        """Estimate, authorize, (escalate), reserve, submit, commit — or default-deny."""
        amount = self._client.cost_estimate(request).total_usd
        decision = self._guard.authorize(request.experiment_type, amount)
        if not decision.allowed:
            return GuardedResult(allowed=False, reason=decision.reason, amount_usd=amount)
        if decision.needs_approval and not self._approval(request, amount):
            self._guard.journal.append("approval_denied", {"amount_usd": amount})
            return GuardedResult(allowed=False, reason="human approval declined", amount_usd=amount)
        reservation = self._guard.budget.reserve(amount)
        if reservation is None:  # pragma: no cover - budget re-checked; guards a race
            return GuardedResult(allowed=False, reason="no budget headroom", amount_usd=amount)
        try:
            handle = self._client.submit(request)
        except Exception:
            self._guard.budget.release(reservation)
            self._guard.journal.append("submit_failed", {"amount_usd": amount})
            raise
        self._guard.budget.commit(reservation)
        self._guard.journal.append(
            "submitted", {"experiment_id": handle.experiment_id, "amount_usd": amount}
        )
        return GuardedResult(
            allowed=True, reason="submitted", amount_usd=amount, experiment_id=handle.experiment_id
        )
