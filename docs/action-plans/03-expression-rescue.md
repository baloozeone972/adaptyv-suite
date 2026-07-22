# Action plan 03 — expression-rescue (I) ⏳ next

Spec I. Diagnose designs that won't express, and propose corrected variants.
Strongest opening: "you published this workflow, I built it."

## Verify first
- The "Improve Protein Expression" guide's recommended chain (NetSolP/SoluProt →
  ESM log-likelihood → SolubleMPNN-style redesign → re-screen).
- Proteinbase expression labels availability + license (ODC-BY).

## Reuses from adaptyv-core
- `seq.validate` = the `validate/` layer (already built for preflight). ✅
- New in core here: `biophysics` (pI, GRAVY, patches, cys, N-glyc, motifs),
  `plm` (ESM log-likelihood, disk cache), `stats` (calibration), `report`.

## Work packages
| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | schemas (Liability, Variant, SequenceReport, CampaignReport) | — | 0.5 |
| L1 | validate/ (reuse preflight) | core.seq | 0.5 |
| L2 | diagnose/ — biophysics + positioned liabilities | core.biophysics | 2 |
| L3 | diagnose/language_model — ESM w/ cache | core.plm | 1 |
| L4 | score/ — LightGBM + isotonic calibration + baselines | L2,L3,Proteinbase | 2.5 |
| L5 | rescue/ — candidate mutations, ranking | L4 | 2 |
| L6 | report + CLI | L1–L5 | 1.5 |

**MVP** = L0+L1+L2+L4 (no rescue) ≈ 6 j·p. Degrades well: L1+L2 useful alone.

## Guardrails
- Calibration matters more than AUC (client reads "0.3" as "3 in 10").
- Rescue variants are "suggested, not validated" — never "improved".
- Report baselines: majority class, liabilities-only, ESM-only, full model.

## Decision needed
- Local solubility model (trained on Proteinbase) vs optional external predictors.
