"""Budget guardrails and a hash-chained audit journal.

Shared by foundry-guard (K) and dbtl-agent (B). The core guarantee: spending is
controlled by **reservation**, not post-hoc accounting, so no sequence of calls can
exceed the budget. Any failure is default-deny.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field

from pydantic import BaseModel

from adaptyv_core.schemas import AssayType


class Policy(BaseModel):
    """The rules an agent cannot talk its way around."""

    max_total_usd: float
    max_per_call_usd: float
    allowed_assays: set[AssayType]
    require_approval_over_usd: float = float("inf")


class Decision(BaseModel):
    """The outcome of an authorization check."""

    allowed: bool
    reason: str
    needs_approval: bool = False


class BudgetExceededError(RuntimeError):
    """Raised on an attempt to commit more than was reserved."""


@dataclass
class Budget:
    """Reservation-based budget. Invariant: spent + reserved <= max_total_usd."""

    max_total_usd: float
    _spent: float = 0.0
    _reserved: dict[str, float] = field(default_factory=dict)

    @property
    def spent(self) -> float:
        """Committed spend so far."""
        return self._spent

    @property
    def available(self) -> float:
        """Headroom left after spend and outstanding reservations."""
        return self.max_total_usd - self._spent - sum(self._reserved.values())

    def reserve(self, amount: float) -> str | None:
        """Hold `amount` if there is headroom; return a reservation id or None."""
        if amount < 0 or amount > self.available:
            return None
        rid = uuid.uuid4().hex[:12]
        self._reserved[rid] = amount
        return rid

    def commit(self, reservation_id: str) -> float:
        """Turn a reservation into committed spend. Never exceeds the reserved amount."""
        amount = self._reserved.pop(reservation_id)
        self._spent += amount
        return amount

    def release(self, reservation_id: str) -> None:
        """Cancel a reservation (e.g. the call failed)."""
        self._reserved.pop(reservation_id, None)


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One tamper-evident journal entry."""

    index: int
    event: str
    data: dict[str, object]
    prev_hash: str
    hash: str


def _entry_hash(index: int, event: str, data: dict[str, object], prev_hash: str) -> str:
    payload = json.dumps(
        {"index": index, "event": event, "data": data, "prev_hash": prev_hash}, sort_keys=True
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class AuditJournal:
    """Append-only, hash-chained log. Any edit breaks `verify()`."""

    _entries: list[AuditEntry] = field(default_factory=list)

    def append(self, event: str, data: dict[str, object]) -> AuditEntry:
        """Append an entry chained to the previous one's hash."""
        prev = self._entries[-1].hash if self._entries else "genesis"
        index = len(self._entries)
        entry = AuditEntry(index, event, data, prev, _entry_hash(index, event, data, prev))
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        """Recompute the chain; return False if any entry was altered or reordered."""
        prev = "genesis"
        for i, entry in enumerate(self._entries):
            if entry.index != i or entry.prev_hash != prev:
                return False
            if entry.hash != _entry_hash(entry.index, entry.event, entry.data, entry.prev_hash):
                return False
            prev = entry.hash
        return True

    def entries(self) -> list[AuditEntry]:
        """A copy of the journal."""
        return list(self._entries)


@dataclass
class Guard:
    """Policy + budget + audit. `authorize` is default-deny."""

    policy: Policy
    budget: Budget
    journal: AuditJournal = field(default_factory=AuditJournal)

    def authorize(self, assay: AssayType, amount_usd: float) -> Decision:
        """Decide whether a call may proceed, recording the decision."""
        decision = self._evaluate(assay, amount_usd)
        self.journal.append(
            "authorize",
            {
                "assay": assay.value,
                "amount_usd": amount_usd,
                "allowed": decision.allowed,
                "needs_approval": decision.needs_approval,
                "reason": decision.reason,
            },
        )
        return decision

    def _evaluate(self, assay: AssayType, amount_usd: float) -> Decision:
        if assay not in self.policy.allowed_assays:
            return Decision(allowed=False, reason=f"assay {assay.value!r} not in scope")
        if amount_usd > self.policy.max_per_call_usd:
            return Decision(allowed=False, reason="exceeds per-call cap")
        if amount_usd > self.budget.available:
            return Decision(allowed=False, reason="exceeds remaining budget")
        needs = amount_usd > self.policy.require_approval_over_usd
        return Decision(allowed=True, reason="within policy", needs_approval=needs)
