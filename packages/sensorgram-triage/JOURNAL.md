# Journal de bord — sensorgram-triage

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec H)

**Goal:** attack the day 16–21 data-review phase — auto-sort curves and quantify
how much human review can be safely removed. Builds on adaptyv-kinetics (G).

**Built:** features (per-replicate via kinetics + protein-level K_D disagreement);
a dependency-free numpy logistic regression (deterministic); a synthetic labelled
dataset; the delegation analysis (grouped stratified split, curve, Brier); triage
into green/orange/red with reasons; HTML report with the delegation figure; Typer
CLI (calibrate / triage).

**Commands used:**
```bash
uv sync --all-packages
uv run sensorgram-triage calibrate --max-fnr 0.02 --report delegation.html
uv run sensorgram-triage triage package.zip --report triage.html
make all
```

**Decisions & fixes (measured, not guessed):**
- **Perfect separation first** (Brier 0, step-function curve): synthetic artifacts
  are too easy. Fix 1: good binders span a range of measurement noise so the noisiest
  overlap the problematic ones. Fix 2 (the real bug): the grouped split took names
  from the end of a class-sorted list, so the test set was all-good — made stratified
  by class. Result: honest curve — ~60% auto-approved at 0% FNR, Brier ~0.01.
- Removed a dead `fit_on`; covered every reason/pile branch with direct unit tests.

**Status:** ✅ 189 tests (suite total), 100% coverage, mypy --strict clean, ruff clean.
Demo: clean binder → green, non-binder/incomplete/spike → red with correct reasons.

**Next:** learning-curve estimate (labels needed for a target FNR); a Streamlit
review UI; then spec D (insilico-bench).
