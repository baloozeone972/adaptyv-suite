# Action plan 08 — binder-triage (A) ⏳ planned

Spec A. Replace "top-N by a single score" with constrained selection that
maximizes expected binders (or information) for a budget. The heaviest project.

## Verify first
- Proteinbase campaign data quality and the **selection-bias caveat**: published
  designs already passed an in-silico filter, so the binding model learns
  "bind | passed filter". Must be written in limitations and said in the Loom.

## Reuses from adaptyv-core
- `seq.validate`, `biophysics`, `plm` (ESM w/ cache), `stats` (grouped CV,
  bootstrap, calibration), `pricing` (plate tiers), `proteinbase`, `foundry`,
  `report`.

## Work packages (abridged)
| Lot | Content | Effort |
|---|---|---|
| L1 | data/ Proteinbase ingest+normalize | 2 |
| L2 | features/ biophysics + ESM | 2 |
| L3 | predict/expression + calibration | 2 |
| L4 | predict/binding | 1.5 |
| L5 | select/ objective + diversity (submodular greedy, DPP, ILP) + plate tiers | 3 |
| L6 | evaluate/ leave-one-campaign-out backtest + CIs | 2.5 |
| L7 | api + CLI + report | 1.5 |

**MVP** ≈ 11 j·p. If time runs short, ship only expression prediction (L1–L3) —
i.e. converge to expression-rescue (I).

## Method rigor (non-negotiable)
- CV grouped by sequence cluster (≥70% id) **and** by campaign, both reported.
- Never a bare number: bootstrap CI + n + baseline (top-ipSAE, random).
- Honest result is the expected result; propose the prospective protocol.
