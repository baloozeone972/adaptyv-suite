# mosaic-loop — technical documentation

Recalibrate Mosaic's predicted objective terms with Adaptyv's measurements, and report
per-term drift.

## Module map

```
schemas.py    ObjectiveTerm, ASSAY_TO_TERM, DesignMeasurement, Calibration, DriftReport
stats.py      pearson, spearman (numpy)
calibrate.py  calibrate_term, analyze (+ objective recomposition)
data.py       synthetic paired (predicted, measured) terms
report.py     drift table (self-contained HTML)
cli.py        analyze
```

## The one-to-one map

`ASSAY_TO_TERM` links Adaptyv assays to Mosaic terms: affinity↔binding,
solubility↔expression, stability↔thermostability. That correspondence is what makes a
direct measurement→objective feedback possible.

## Calibration

For each term, `calibrate_term` fits `measured ≈ slope·predicted + intercept` (OLS) and
records Pearson, Spearman, and the post-fit MAE. **Drift = 1 − Spearman**: it captures
whether the predicted term *ranks* designs the way the measurement does — which
calibration (a monotonic rescale) cannot fix, so it is the honest signal of a bad proxy.

## Objective realignment

`analyze` builds three weighted composites — from raw predicted terms, from calibrated
terms, and from the measurements — and reports `Spearman(raw, measured)` vs
`Spearman(calibrated, measured)`. Because raw terms live on different scales (a pLDDT-like
0–1 vs a pK_D vs a °C), the raw weighted sum mixes them incoherently; calibration puts
them on a common (measured) scale, so the calibrated composite agrees better with reality.

## Testing

100% coverage: correlation helpers (incl. degenerate), a linear-relation recovery, the
single-point safe path, the synthetic drift pattern (affinity high, stability poor), and
that recalibration never lowers objective agreement. Report + CLI covered.

## Not built (documented)

A live Mosaic adapter (reading its actual objective-term API and writing back calibrated
terms) needs Mosaic installed; here the loop runs against a synthetic, declared export.
The mapping, calibration and drift analysis are Mosaic-agnostic and transfer unchanged.

## Domain model

Bounded context: **External-Model Feedback** — a standalone
**Customer/Supplier** consumer of the shared base plus a declared synthetic
export; Mosaic's objective terms are referenced, not owned, by this suite.
Core aggregates: `DesignMeasurement`, `Calibration`, `DriftReport`. No
relationship to the Foundry ACL. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
