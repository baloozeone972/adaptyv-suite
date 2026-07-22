# Action plan 06 — campaign-planner (J) ⏳ planned

Spec J. A solver that, given a budget and objective, enumerates valid experiment
configurations — including two-step sequential strategies the web configurator
can't express — and ranks them.

## Verify first
- Pricing grid, plate tiers {24,48,96,192,384,768}, assay prices/durations, the
  20% Proteinbase-publication discount. Calibrate against
  `POST /experiments/cost-estimate` when a token is available.

## Reuses from adaptyv-core
- `pricing` (grid, tiers, discounts — shared with binder-triage A),
  `foundry` (live cost-estimate), `stats` (Monte-Carlo CIs).

## Work packages
| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | schemas (AssayType, PlateTier, Step, Strategy, StrategyEvaluation) | core | 0.5 |
| L1 | pricing/ — grid, validity rules, API calibration | L0 | 1.5 |
| L2 | strategy/ — enumerate + sequential (2-step) | L1 | 1.5 |
| L3 | strategy/simulate — Monte-Carlo yield w/ CI | L0 | 1.5 |
| L4 | optimize/rank — multi-objective, Pareto front | L2,L3 | 1 |
| L5 | explain/ narrative + CLI | L4 | 1 |

**MVP** ≈ 5 j·p (fastest project).

## Positioning
Thin on ML — best framed as a **module of binder-triage (A)** or the sales-facing
front door. The interesting result: from what expected failure rate does the
two-step (cheap expression filter → affinity on survivors) become worth it.
