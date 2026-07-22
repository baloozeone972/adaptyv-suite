# Journal de bord — dbtl-agent

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec B, governance-first)

**Goal:** an autonomous DBTL loop — the most-submitted idea, so shipped
**governance-first**: hard budget, tamper-evident audit, anti-monoculture. Ties the
suite together (guard + binder-triage + pricing).

**Built:** strict `SimulatedOracle`; per-family `ClusterBelief` with Thompson
sampling; `run_campaign` (guarded, audited, diversity-aware, learning loop) and a
`random_baseline` control; Typer CLI.

**Commands used:**
```bash
uv sync --all-packages
uv run dbtl-agent run --budget 20000 --batch 24 --rounds 6
make all
```

**Decisions & findings (measured, not guessed):**
- Hit rate looked flat at first — correctly: good families **deplete** as they are
  tested. So the honest performance metric is vs a **random baseline**: the agent
  captures **~20–30% more binders** at equal budget (e.g. 47 vs 36, +31%).
- Kept diversity as a first-class constraint: every round stays at ~6 families
  (identity ~0.15), so the loop never converges to a monoculture (the TREM2 failure).
- Budget is reservation-guarded, so it is respected 100% (guaranteed, not averaged);
  the round-by-round audit chain verifies.
- Needed `binder-triage = { workspace = true }` in root `tool.uv.sources` (first
  member→member dependency in the workspace).

**Status:** ✅ suite total 266 tests, 100% coverage, mypy --strict clean, ruff clean.
Demo: budget respected True, audit valid True, diverse, +31% vs random.

**Next:** real async Foundry execution (webhooks, multi-week resume), token
attenuation, a richer surrogate than per-family Beta.
