# adaptyv-kinetics — technical documentation

Reads Adaptyv's binding data package, re-fits the kinetics independently, flags
artifacts, and renders a report — in one command. An **independent verifier**, not
a competitor to Adaptyv's fitting pipeline.

## On-disk schema (verified against the live docs)

```
package/
├── raw_data/    <name>_<replicate>_<concentration>.csv   columns: t (s), y (nm)
├── fit_data/    same naming — Adaptyv's fitted curves
├── aux/replicate_info.csv   name, replicate, method(BLI|SPR), MAE, rel_MAE, rmax_estimate
├── kinetics/    (computed parameters)
└── blanks/      raw_data/, figures/, run_mapping.csv
```

Names may contain underscores, so the parser matches each raw file to a known
`(name, replicate)` pair by **longest prefix**, and the remainder is the concentration.

## Module map

```
io/       package (façade, from_zip/from_dir), parsers, synthetic (generator = validation harness)
models/   langmuir (1:1 response, split inference), fitting (global fit + bootstrap CI)
qc/       features (shape descriptors), rules (artifact catalog, verdict)
report/   plots (matplotlib overlay), html (self-contained), export (csv/parquet/json)
cli.py    synth / report / refit / qc / compare
```

## Fitting

Langmuir 1:1. Association (`t ≤ t_a`) and dissociation (`t > t_a`) with `k_on`,
`k_off`, `R_max` shared across a replicate's concentration series, and a free
baseline per curve. Optimisation: `scipy.least_squares` (Trust Region Reflective),
rate constants log-scaled for positivity, initial guess clipped inside the box.

- **Split inference** (`t_a`): peak of a **median-filtered** curve — spike-robust
  and, unlike a moving average, does not shift a broad peak (a boxcar biased K_D by
  ~5%; the median filter fixed it).
- **Bootstrap CI on K_D**: residual resampling, refit each draw, 95% percentile.
- Recovery: exact data <1%; realistic noise <15% median when dissociation is adequate.

## QC catalog

Split-independent descriptors → interpretable rules: `LOW_SNR` (crit),
`INCOMPLETE_DISSOCIATION` (crit, <10% decay → k_off unidentifiable), `SPIKE` (warn),
`POOR_FIT` (warn). Verdict: reject on any critical, review on any warning, else pass.
Baseline-drift detection is deliberately not shipped (unreliable without the run's
known split) — see `limitations.md`.

## Independent verification

`compare_fits()` puts the re-fit next to the package's reported values (R_max
estimate, rel_MAE). Large R_max differences are expected when concentrations don't
saturate binding — surfaced, not hidden.

## Security

`from_zip` rejects any archive member resolving outside the temp dir (zip-slip).

## Testing

100% coverage. The synthetic generator doubles as the validation harness (known
true parameters); a `hypothesis` test asserts the fitter stays finite and never
crashes across varied K_D / noise / seed.

## Domain model

Bounded context: **Kinetics Analysis** — the suite's **core domain** (the deepest,
most differentiating logic: `Trace`, `KineticFit`, `QCFlag`, `TraceVerdict`).
Consumes a *downloaded* binding data package (a file, parsed by `io/`), not a live
Foundry call — so it has no direct relationship to the Foundry ACL in
`adaptyv-core.foundry`. It is upstream of two contexts via **Customer/Supplier**:
`sensorgram-triage` (Curve Triage) depends on its fits, and `protviz`
(Visualisation, an **Open Host Service**) is depended on *by* this package for
figures. See [the DDD doc](../../../docs/architecture/domain-driven-design.md).
