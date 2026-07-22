# Journal de bord — expression-rescue

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec I)

**Goal:** implement the expression workflow Adaptyv published but nobody built.
Reuses `preflight`'s validation as the `validate/` layer; introduces the shared
`adaptyv-core.biophysics` module (also for A and H).

**Built:**
- `adaptyv-core.biophysics` — GRAVY (Kyte-Doolittle), hydrophobic patches
  (sliding window, merged), net charge, isoelectric point (bisection, EMBOSS pKa),
  residue fraction. 100% covered.
- `expression-rescue`: schemas (Liability, Variant, SequenceReport, CampaignReport,
  RiskTier); `diagnose/liabilities` (10 positioned liabilities); `score/risk`
  (heuristic tier); `rescue/mutations` (≤3 conservative mutations); `report`
  (HTML via core.report); Typer CLI (check / estimate / rescue).

**Commands used:**
```bash
uv sync --all-packages
uv run expression-rescue check designs.fasta --assay affinity --has-target
uv run expression-rescue estimate designs.fasta --price-per-protein 169
uv run expression-rescue rescue designs.fasta --out corrected.fasta
make all
```

**Decisions & fixes (measured, not guessed):**
- Liabilities run **per chain with position offsets** so no motif is invented at a
  chain junction.
- Blocked sequences (fail validation) skip diagnosis; the CLI shows `BLOCK` with
  the blocking codes rather than a misleading `LOW / clean`.
- Regex `{n,}` quantifiers moved to f-strings (ruff UP031); `net_charge` sums given
  an explicit `0.0` start so mypy keeps the return `float`.
- Kept the tool honest: risk tier is a heuristic, variants are "suggested"; the
  calibrated model and ESM re-scoring are documented as needing Adaptyv's data.

**Status:** ✅ 139 tests, 100% coverage, mypy --strict clean, ruff clean.
Demo: a clean binder → LOW, an agent-style design → HIGH (8 liabilities), a
too-short design → BLOCK; rescue proposes `C2S, I8S, N15Q`.

**Next:** wire ESM log-likelihood + a Proteinbase-trained calibrated model when
their data is available; or move to spec L (adaptyv-pipeline).

---

## 2026-07-22 (later) — rescue deepened

- `Variant` now carries `risk_score_before`/`risk_score_after`: rescue re-diagnoses
  the mutated sequence, so it reports the actual score drop rather than assuming the
  correction helped (`score_delta`).
- Rescue honours **interface positions** (`--interface 10,11,45`): those are never
  mutated. Substitutions are finer — branched aliphatics I/L/V/M → T, others → S.
- Still green at 100% coverage.
