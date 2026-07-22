# Action plan 12 — mosaic-loop (N) ⏳ planned · ⭐⭐

Spec N (source: `24-spec-N-mosaic-loop.md`). Close the loop: Adaptyv's measurements
recalibrate the terms of Mosaic's multi-objective function, round after round.

## The one-to-one match
Mosaic optimises **affinity, solubility, stability**; Adaptyv measures **binding,
expression, thermostability**. The objective terms and the assays coincide exactly
— the only such match in the ecosystem. Mosaic also won on TREM2 (66.7% hit rate,
best binder 1.11 nM) and Nipah.

## Verify first
- Mosaic's public interface (JAX wrapper composing Boltz/AF2/Protenix/MPNN/ESM),
  its objective-term API, and how to export a candidate panel.

## Reuses from adaptyv-core / suite
- `binder-triage` (A) for budgeted panel selection, `foundry` client,
  `stats` (drift between predicted term and measured value), `report`.

## Work packages
| Lot | Content | Effort |
|---|---|---|
| L0 | schemas: objective term, measurement, calibration record | 0.5 |
| L1 | Mosaic export → budgeted Adaptyv panel | 2 |
| L2 | ingest results, map assay → objective term | 1.5 |
| L3 | recalibrate predicted terms on measurements (per term) | 2 |
| L4 | recompose objective, prediction/measurement drift report | 1.5 |

**MVP** ≈ 8 j·p. Honest framing: report how far each predicted term drifts from
measurement, even when recalibration barely moves the ranking.
