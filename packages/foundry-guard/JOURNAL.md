# Journal de bord — foundry-guard

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec K)

**Goal:** a guardrail proxy between an autonomous agent and the Foundry API —
spend caps, scope allow-lists, human escalation, tamper-evident audit — that the
agent cannot bypass. Introduces the shared `adaptyv-core.guard` (also for B).

**Built:** `adaptyv-core.guard` (Policy, Decision, reservation-based Budget,
hash-chained AuditJournal, default-deny Guard); `foundry-guard` (GuardedLab proxy
over a FoundryClient, ApprovalGate, offline demo transport, CLI).

**Commands used:**
```bash
uv sync --all-packages
uv run foundry-guard demo --budget 3000
make all
```

**Key guarantee, tested:** spending is **reservation-based**, so no call sequence
can exceed the budget. A `hypothesis` property test fuzzes reserve/commit/release
and asserts `spent + reserved ≤ cap` always. The audit chain detects both content
tampering and broken links.

**Demo:** small affinity ALLOW; expression DENY (scope); 20-design DENY (per-call
cap); 10-design DENY (needs approval, default-deny); another small ALLOW. Spent
$1,859 of $3,000 — never exceeded; audit chain valid (8 entries).

**Status:** ✅ suite total 242 tests, 100% coverage, mypy --strict clean, ruff clean.

**Next:** MCP HTTP shell + token attenuation (`POST /tokens/attenuate`); persistent
audit journal; then spec A (binder-triage).
