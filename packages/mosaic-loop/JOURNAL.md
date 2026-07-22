# Journal de bord — mosaic-loop

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec N)

**Goal:** close Mosaic's loop — feed Adaptyv measurements back to recalibrate its
predicted objective terms and surface which terms track reality. External system, so
built as an honest adapter + analysis against a synthetic (declared) export.

**Built:** schemas (ObjectiveTerm, the one-to-one ASSAY_TO_TERM map, DesignMeasurement,
Calibration, DriftReport); numpy correlation helpers; per-term calibration + composite
objective realignment; synthetic data; HTML report; Typer CLI.

**Commands used:**
```bash
uv sync --all-packages
uv run mosaic-loop analyze --report drift.html
make all
```

**Design choices (measured, not guessed):**
- **Drift = 1 − Spearman(predicted, measured)** is the honest signal: it measures rank
  agreement, which a linear recalibration cannot fix — so it flags genuinely bad proxies.
- Recalibration puts terms on a common measured scale, so the calibrated composite
  agrees better with the measured composite (demo: 0.35 → 0.51).
- Synthetic set built so affinity tracks well (ρ~0.96), solubility moderately (~0.54),
  and stability is a poor proxy (~0.0, flagged) — driven by a hidden confounder.

**Status:** ✅ suite total 280 tests, 100% coverage, mypy --strict clean, ruff clean.

**Next:** a live Mosaic adapter (real objective-term API, write-back), non-linear
calibration, user-supplied weights.
