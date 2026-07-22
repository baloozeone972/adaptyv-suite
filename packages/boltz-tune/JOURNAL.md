# Journal de bord — boltz-tune

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec M, research harness)

**Goal:** answer honestly whether fine-tuning Boltz-2's affinity head on Adaptyv data
helps, and how much data a real gain needs. The spec's highest-risk idea — so built as a
**reproducible harness + honest quantified result**, not a trained model.

**Built:** schemas (TrainingObservation, LearningCurve with predict/n_for, TuneResult);
`fit_curve` (scipy power-law) + `evaluate` (four honest verdicts); synthetic training-size
sweep (declared); Typer CLI.

**Commands used:**
```bash
uv sync --all-packages
uv run boltz-tune evaluate --target-lift 0.05
make all
```

**Decisions & findings (measured, not guessed):**
- The curve `score(n) = plateau − coef·n^(−alpha)` recovers the true plateau (0.718 vs
  0.72) once a wide enough size range is swept (added n=1600 so the plateau is constrained).
- All four verdicts are reachable and tested: already-helps (+0.02), needs-~6×-more-data
  (+0.05), unreachable (+0.10), never-beats-base (base 0.80). The default +0.05 gives the
  headline: **~6× more data for a meaningful gain**.
- Framed as research: the curve is synthetic and declared; the real numbers need Adaptyv's
  data + compute (documented in `docs/limitations.md`).

**Status:** ✅ suite total 285 tests, 100% coverage, mypy --strict clean, ruff clean.

**Next:** real fine-tuning on Proteinbase with grouped splits; CIs on the extrapolation;
compare against the current interface-metric filter, not just the base model.
