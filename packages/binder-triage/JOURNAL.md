# Journal de bord — binder-triage

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec A, MVP)

**Goal:** replace "top-N by a single score" with constrained, diversity-aware
selection under a plate budget — the heaviest spec, shipped as its defensible core.

**Built:** k-mer similarity; a clustered synthetic pool with a per-family predictor
bias; two selection strategies (naive top-N, submodular diverse-greedy); evaluation
(expected/true binders, monoculture identity, families, cost via `adaptyv-core.pricing`);
Typer CLI.

**Commands used:**
```bash
uv sync --all-packages
uv run binder-triage select --k 24 --diversity 0.8
make all
```

**Decisions & fixes (measured, not guessed):**
- First attempt (8 families, k=48) diluted the monoculture signal — top-N was forced
  across families. Tightened to fewer/larger families and k=24 (a plate tier), so
  top-N can collapse into one family: identity 0.72 vs 0.48, families ~1 vs ~4.5.
- The honest headline is **robustness, not more binders**: diverse trades a little
  predicted yield for a **better worst case** (true binders 3.8 → 4.5) — insurance
  against per-family predictor bias, matching the TREM2 monoculture finding.
- Stated the **selection-bias caveat** for real data in `docs/limitations.md`.

**Status:** ✅ suite total 253 tests, 100% coverage, mypy --strict clean, ruff clean.

**Next:** a real calibrated binding model (LightGBM+ESM on Proteinbase, grouped CV),
DPP/ILP selection, expression-aware two-stage; then spec B (dbtl-agent).
