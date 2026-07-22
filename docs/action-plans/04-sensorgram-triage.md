# Action plan 04 — sensorgram-triage (H) ⏳ planned

Spec H. Auto-sort binding curves into publishable / review / re-run, attacking
the day 16–21 data-review phase (a quarter of the delivery time).

## Depends on
- **adaptyv-kinetics (G)** for parsing, re-fit residuals, and the artifact
  catalog. H never re-implements fitting. Build G first.

## Reuses from adaptyv-core
- `stats` (calibration, thresholds), `report`.

## Work packages
| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | schemas | G | 0.5 |
| L1 | features/ — shape, residuals, consistency, controls | G | 2.5 |
| L2 | rules/ — reuse G's catalog | G | 0.5 |
| L3 | labelled-set generation (simulation + Proteinbase weak labels) | G | 2 |
| L4 | model/ — LightGBM or logistic + isotonic calibration | L1,L3 | 2 |
| L5 | **thresholds.py — cost/benefit delegation curve (the central figure)** | L4 | 1.5 |
| L6 | review/ — Streamlit review UI + label logging | L4 | 1.5 |

**MVP** = L0–L5 ≈ 9 j·p (excl. G). G+H together ≈ 16–17 j·p.

## The deliverable is one figure
Auto-approved fraction vs false-negative rate: "at 2% FNR, 61% of curves need no
human eye." Positioned as a **calibratable harness**, not a calibrated model;
quantify how many internal labels would calibrate it.
