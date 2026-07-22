# foundry-guard — technical documentation

A policy-enforcing proxy over the Foundry API. The guard engine lives in
`adaptyv-core.guard` (shared with dbtl-agent B); this package is the Foundry-facing
wrapper.

## Module map

```
adaptyv-core.guard   Policy, Decision, Budget (reservation), AuditJournal, Guard
proxy.py             GuardedLab: wraps a FoundryClient; ApprovalGate; auto_deny
_demo.py             an in-process fake Foundry transport (offline demo)
cli.py               demo
```

## The submission pipeline

```
cost_estimate ─▶ guard.authorize(assay, amount) ─┬─ denied ─▶ default-deny (budget untouched)
                                                 └─ allowed ─▶ needs_approval?
                                                       ├─ yes & gate denies ─▶ deny + audit
                                                       └─ ok ─▶ budget.reserve ─▶ submit
                                                                     ├─ raises ─▶ release + audit + re-raise
                                                                     └─ ok ─▶ commit + audit "submitted"
```

## Budget: reservation, not accounting

`Budget` keeps `spent` and a map of outstanding `reserved` amounts. Invariant:
`spent + Σreserved ≤ max_total`. `reserve(amount)` returns an id only if
`amount ≤ available`; `commit(id)` moves the reserved amount to `spent`;
`release(id)` cancels. Because headroom is claimed before the call, concurrent or
sequential calls cannot collectively overspend. A `hypothesis` test fuzzes
reserve/commit/release sequences and asserts the invariant.

## Audit: hash chain

Each `AuditEntry` stores `sha256(index ‖ event ‖ data ‖ prev_hash)`. `verify()`
recomputes the chain from a `"genesis"` seed and returns False if any entry's
index, `prev_hash`, or content was altered (tests cover both content tampering and
a broken chain link).

## Policy

`Policy(max_total_usd, max_per_call_usd, allowed_assays, require_approval_over_usd)`.
`Guard.authorize` is **default-deny**: scope first, then per-call cap, then budget
headroom, then the approval flag. Every decision is journaled.

## Testing

100% coverage. Proxy paths: allow/commit, scope deny, per-call deny, budget deny,
approval required/granted, submit failure (budget released), and a
budget-exhaustion sequence. The network transport is out of scope (the demo uses a
fake); the MCP HTTP shell is future work.
