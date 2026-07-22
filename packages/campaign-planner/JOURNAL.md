# Journal de bord — campaign-planner

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec J)

**Goal:** given a budget and objective, enumerate valid experiment strategies —
including two-step sequential ones the web configurator can't express — and rank
them. Introduces the shared `adaptyv-core.pricing` module (also for A).

**Built:** `adaptyv-core.pricing` (plate tiers, per-assay unit prices, publication
discount, billing by whole tier); `campaign-planner` (Monte-Carlo yield+cost sim,
direct vs two-step strategies, budget-aware ranking, crossover analysis, CLI).

**Commands used:**
```bash
uv sync --all-packages
uv run campaign-planner plan --n 96 --p-express 0.4 --p-bind 0.15 --budget 20000
make all
```

**Decisions & fixes (measured, not guessed):**
- Direct and two-step give the **same expected binders**, so ranking by yield alone
  tied. Added **cost** as the tiebreaker — that is what surfaces the two-step's real
  advantage (same yield, lower cost when expression is unreliable).
- Two-step cost is **stochastic** (survivors → affinity tier), so it's simulated,
  not point-estimated; duration is the sequential sum (a real downside).
- Typer registered the single command as a callback; added a group `@app.callback()`
  so `plan` is an explicit subcommand.

**Status:** ✅ suite total 221 tests, 100% coverage, mypy --strict clean, ruff clean.
Demo result: at P(express)=0.3, two-step $14,993 vs direct $16,224 (same ~4.3
binders); crossover ≈ 50% — filter first while fewer than half express.

**Next:** screening variants, replicate optimisation, "maximize information"
objective; then spec K (foundry-guard).
