# Journal de bord — adaptyv-kinetics

Logbook with exact commands. Newest entry on top.

---

## 2026-07-21 — Built & green (flagship tool, spec G)

**Goal:** the top-ranked deliverable — read the binding data package, re-fit
independently, QC, report. Bounded scope, its synthetic generator doubles as the
validation harness.

**Verify-first (done before coding):** re-fetched the live "Binding Data Package"
doc and confirmed the on-disk schema — `raw_data/`, `fit_data/`,
`aux/replicate_info.csv` (`name, replicate, method, MAE, rel_MAE, rmax_estimate`),
filenames `<name>_<replicate>_<concentration>.csv`, columns `t` (s) / `y` (nm),
3-decimal rounding. Matched the spec; one addition: names can contain underscores,
so the parser matches raw files by longest known (name, replicate) prefix.

**Built:** schemas (Trace, ReplicateInfo, KineticFit, QCFlag, TraceVerdict);
`io/` (parser + synthetic generator + DataPackage façade); `models/` (Langmuir
1:1 + global fit + bootstrap CI); `qc/` (features + rule catalog); `report/`
(matplotlib plots, self-contained HTML via `adaptyv_core.report`, CSV/Parquet/JSON
export); Typer CLI (`synth`, `report`, `refit`, `qc`). Added `stats` and `report`
modules to `adaptyv-core`.

**Commands used:**
```bash
uv sync --all-packages
uv run adaptyv-kinetics synth --out /tmp/pkg.zip
uv run adaptyv-kinetics qc /tmp/pkg.zip --bootstrap 0
uv run adaptyv-kinetics report /tmp/pkg.zip -o /tmp/report.html
make all   # ruff + mypy --strict + pytest
```

**Debugging that shaped the result (all measured, not guessed):**
1. **K_D recovery biased 13→32 nM under noise.** Root cause: `infer_assoc_end`
   used a raw argmax, and noise moved the association/dissociation split. Fix:
   median filter (spike-robust, does not shift a broad peak like a boxcar does).
2. **Still biased.** Root cause: dissociation window too short (~14% decay) →
   k_off weakly identified. Fix: generator defaults to an adequate dissociation
   (~45% decay). Recovery: exact <1%, noisy median <15%.
3. **decay_fraction depended on the inferred split.** Redefined split-independent:
   `(peak − final)/(peak − baseline)`.
4. **Non-binder not caught.** Raised `SNR_MIN` to 10; non-binders (SNR ~7) now
   flagged `LOW_SNR`, real binders (SNR ~40+) pass.
5. **BASELINE_DRIFT unreliable** with an inferred split (drift moves the peak).
   Dropped as an active rule; drift surfaces as `POOR_FIT`. Documented in
   `docs/limitations.md`.
6. Fixed a scipy "initial guess outside bounds" crash on non-binders (clip p0).

**Status:** ✅ 54 tests pass, mypy --strict clean, ruff clean, 90% coverage.
Demo package → 4 clean binders PASS, non-binder + incomplete REJECT, spike REVIEW;
K_D recovered with bootstrap CIs; HTML report renders with embedded sensorgrams.

**Next:** mass-transport & bivalent models (L3); calibrate QC thresholds on real
labelled data; then spec I (expression-rescue), reusing `preflight`'s validation.

---

## 2026-07-21 (later) — Test hardening + zip-slip fix

- **Security:** `DataPackage.from_zip` now rejects any archive member whose
  resolved path escapes the extraction dir (path traversal / "zip slip"). Tests
  cover `../` and absolute-path members, plus nested-root and empty-zip cases.
- New tests: parser error paths (missing replicate_info, wrong columns, unmatched
  prefix, non-float concentration, underscore-name longest-prefix); package error
  paths; edge cases (single concentration, tiny arrays, flat curve, unknown export
  format); a hypothesis test that the fitter stays finite and never crashes across
  varied K_D/noise/seed. Package at 100% coverage.

---

## 2026-07-21 (demo polish) — compare_fits + report section + cleanup

- Added `compare_fits()` and the `compare` CLI command: independent re-fit vs the
  package's reported values (R_max estimate, rel_MAE) — realises the Loom's
  "independent verifier" beat. The report gained an "Independent verification"
  section with an honest note that large R_max diffs reflect non-saturating
  concentrations (surfaced, not hidden).
- `write_zip` now uses a real temp dir (no leftover `package.dir` beside the zip).
- Loom script + three run-throughs written to `docs/loom-script.md`.
- Suite: 102 tests, 100% coverage, all green.

