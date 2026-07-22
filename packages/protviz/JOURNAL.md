# Journal de bord — protviz

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec O), with the kinetics refactor

**Goal:** the shared visualisation layer for G/A/H/I/D — one object, one function, a
correct figure by default — and prove it by migrating a real tool onto it.

**Built:** `theme` (Okabe-Ito colour-blind-safe palette, `new_axes`, `render` → PNG);
`figures` (sensorgram, kinetic_map with iso-K_D lines, censored_kd, reliability_curve,
hit_rate_at_budget). Every function is **array-in, PNG-out** so there is no dependency
cycle.

**The refactor (the point of the spec):** `adaptyv-kinetics.report.plots.plot_replicate`
now builds `protviz.Series` and calls `protviz.sensorgram`. adaptyv-kinetics depends on
protviz; protviz depends on nothing domain-specific. The kinetics tests still pass
unchanged — behaviour-preserving.

**Commands used:**
```bash
uv sync --all-packages
uv run pytest packages/protviz packages/adaptyv-kinetics
make all
```

**Decisions & fixes:**
- Type the theme with `matplotlib.figure.Figure` / `matplotlib.axes.Axes` (not
  `plt.Figure`, which the stubs don't expose).
- Non-binders are drawn **right-censored** (> LOD), not dropped — the statistically
  honest view of a K_D distribution.

**Status:** ✅ suite total 275 tests, 100% coverage, mypy --strict clean, ruff clean.
First member→member dependency reused (`adaptyv-kinetics → protviz`).

**Next:** migrate sensorgram-triage / insilico-bench plots onto protviz too; add
structure-coloured-by-measurement (Mol*/3Dmol) and SVG output; then N and M.
