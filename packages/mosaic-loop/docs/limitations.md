# Known limitations — mosaic-loop

## No live Mosaic adapter

Mosaic is an external JAX optimiser. Reading its actual objective-term values and writing
recalibrated terms back needs Mosaic installed and its API pinned. Here the loop runs
against a **synthetic, declared** export. The mapping (`ASSAY_TO_TERM`), the calibration,
and the drift analysis are Mosaic-agnostic and would transfer unchanged.

## Linear calibration only

Each term is recalibrated with a linear fit (measured ≈ slope·predicted + intercept). A
non-linear or isotonic calibration would fit curved relationships better; the interface
(`Calibration`) is the same. Note that no monotonic calibration can fix **drift** (rank
disagreement) — that requires a better predicted term, which is the point the report makes.

## Objective weights are assumed

The composite uses default weights (0.5 / 0.3 / 0.2). Mosaic's real weights are user-set;
pass your own to `analyze`. The realignment result depends on them.

## Synthetic result is illustrative

The affinity-good / stability-poor pattern is constructed to show the tool working. On
real data, which terms drift is an empirical finding — and precisely what the loop is for.
