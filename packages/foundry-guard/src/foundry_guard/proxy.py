"""The guardrail proxy: enforce policy on every Foundry call the agent makes.

The agent does not have to cooperate. Every submission goes through: cost estimate
→ authorize (scope + per-call + budget) → human escalation if required → reserve →
create-and-confirm → commit → audit. Any failure is default-deny and the budget is
never touched. Spending is reservation-based, so no call sequence can exceed the cap.

Submission uses the real API's one-shot `auto_confirm=True` path
(`FoundryClient.create_experiment`, which sets `auto_accept_quote` + `skip_draft`)
so the entire spend happens at one call the guard can gate atomically — see
`adaptyv_core.foundry` for why that path was chosen over the granular
create/submit/confirm-quote sequence.
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

    def submit(self, request: AssayRequest, name: str) -> GuardedResult:
        """Estimate, authorize, (escalate), reserve, create+confirm, commit — or deny.

        `name` is required by the real API (`CreateExpRequest.name`) — pass a
        human-readable label for the experiment.
        """
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
            handle = self._client.create_experiment(request, name, auto_confirm=True)
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
