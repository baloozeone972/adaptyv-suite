# Journal de bord — insilico-bench

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec D)

**Goal:** a reproducible harness measuring which in-silico scores predict wet-lab
outcome — a tool, not a one-off analysis.

**Built:** schemas (DesignRecord, MetricScore with CI, MetricReport); a synthetic
dataset generator (declared) + CSV loader/writer; numpy metrics (AUC-ROC via
Mann-Whitney, average precision, Spearman, hit-rate@k) with a **paired** bootstrap;
per-score / per-campaign analysis; an HTML report with the hit-rate@k figure; Typer
CLI (synth / run).

**Commands used:**
```bash
uv sync --all-packages
uv run insilico-bench synth --out designs.csv
uv run insilico-bench run designs.csv --out report.html
make all
```

**Decisions & fixes (measured, not guessed):**
- **PR-AUC bug:** a recall-trapezoid gave 0.5 for a perfect ranking (it skips the
  recall 0→first-positive segment). Switched to the standard **average precision**
  `Σ precision·Δrecall`, which is 1.0 for perfect.
- Bootstrap resamples **row indices**, not values, to preserve score/label pairing.
- Synthetic scores built with known, differing power (ipSAE > ipTM > pLDDT) so the
  harness is verifiable; every report stamped synthetic. Selection bias called out
  in `docs/limitations.md`.

**Status:** ✅ suite total 205 tests, 100% coverage, mypy --strict clean, ruff clean.
Demo result (synthetic): ipSAE AUC-ROC ~0.78, Spearman ~0.9; pLDDT ~random.

**Next:** calibration (ECE), leave-one-campaign-out, method effects, score
combination; then spec J (campaign-planner).
