# Action plan 09 — dbtl-agent (B) ⏳ planned

Spec B. Autonomous closed-loop DBTL campaign (design → cost-estimate → submit →
await KDs → relearn → next round) with budget guardrails and audit.

## ⚠️ Strategic warning
This idea is written verbatim in Adaptyv's most-read blog post — it is the
project most other candidates will submit. **Differentiation is the governance
layer, not the loop.** Ship it only as a governance-first extension, never bare.

## Reuses from adaptyv-core
- `guard` (budget + hash-chained audit — shared with foundry-guard K),
  `foundry` (webhook HMAC, token attenuation), `stats`, `plm`.
- `binder-triage (A)` for the selection policy (reused, not rebuilt).

## Work packages (abridged)
| Lot | Content | Effort |
|---|---|---|
| L1 | policy/ budget, guardrails, token attenuation | 2.5 |
| L2 | lab/simulator — Proteinbase oracle (strict mode default) | 2 |
| L3 | lab/foundry + webhooks (HMAC, queue) | 2 |
| L4 | loop/ orchestrator, persistence (SQLite), resume | 2.5 |
| L5 | strategy/ selection, Bayesian update, explore/exploit | 3 |
| L6 | audit/ append-only journal, replay | 1 |

**MVP** = L1+L2+L4+L5(simplified)+L6 ≈ 11 j·p.

## Non-negotiables
- `dry_run=True` default; real execution needs an explicit flag **and** an
  attenuated token. Integration tests run fully offline.
- Strict simulator mode default (only score among already-tested designs of the
  chosen campaign) — that's what makes the backtest valid.
- Anti-monoculture diversity constraint per round (TREM2: agents converged,
  pairwise identity 28.1% vs 22.4%, p=0.0002).
- Budget respected must be **100%**, or the guardrail is broken — property-tested.
