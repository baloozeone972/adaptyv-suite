# Action plan 11 — protviz (O) ⏳ planned · ⭐⭐

Spec O (source: `25-spec-O-protviz.md`, `21-visualisation-outils-et-principes.md`).
A visualisation library for experimentally-validated protein design: one object,
one function, a correct figure by default.

## Why it fits now
It is the **visible layer of G/A/H/I/D**. The kinetics report plots
(`adaptyv_kinetics.report.plots`) are its embryo. The natural trigger to build it
is the second tool that needs the same figures (H reuses sensorgram overlays;
D/A need calibration and hit-rate@budget plots).

## Reuses from adaptyv-core
- `report` (self-contained HTML embedding). protviz provides the figures; core
  assembles them into a document.

## Components (one figure each, correct defaults)
- sensorgram + fit overlay (extract from `adaptyv-kinetics`)
- kinetic map (k_on vs k_off, iso-K_D lines)
- censored K_D distribution (non-binders as censored data)
- reliability / calibration curve, hit-rate@budget
- structure coloured by an **experimental measurement** (Mol*/3Dmol export)

## Work packages
| Lot | Content | Effort |
|---|---|---|
| L0 | figure API + theme (light/dark, colour-blind-safe palette) | 1 |
| L1 | sensorgram/kinetics figures (migrate from adaptyv-kinetics) | 1.5 |
| L2 | selection/calibration figures | 1.5 |
| L3 | structure colouring export | 1 |
| L4 | docs + gallery | 1 |

**MVP** ≈ 6 j·p. First refactor step: move `adaptyv_kinetics/report/plots.py`
into protviz and depend on it, so both tools share one figure implementation.
