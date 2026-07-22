# Journal de bord — adaptyv-suite (racine)

Suite-wide generation log. Each package also keeps its own `JOURNAL.md` with
finer detail. Newest entry on top.

---

## 2026-07-22 (N, M) — the backlog is complete

- **N — mosaic-loop**: feed Adaptyv measurements back to recalibrate Mosaic's predicted
  objective terms; drift = 1 - Spearman flags poor proxies (synthetic demo: affinity
  tracks, stability doesn't; objective agreement 0.35 -> 0.51 after recalibration).
- **M — boltz-tune**: a learning-curve harness (framed as research). Fits
  score(n)=plateau-coef*n^-alpha and extrapolates the data a target gain needs — honest
  headline: ~6x more data for +0.05 over the base model.
- Suite now: **285 tests, 100% coverage, all green.** **Thirteen tools built — every
  specced project (C, G, I, H, D, J, K, A, B, L, O, N, M) is complete.**

---

## 2026-07-22 (O) — shared visualisation layer: protviz

- **O — protviz built**: array-in / PNG-out figure primitives (sensorgram, kinetic
  map, censored K_D, reliability, hit-rate@budget) on one colour-blind-safe theme.
- **Proved the shared layer**: refactored `adaptyv-kinetics` to draw its sensorgram
  via `protviz.sensorgram` (kinetics → protviz, no cycle); kinetics tests unchanged.
- Suite now: **275 tests, 100% coverage, all green.** Eleven tools built; only N, M
  (mosaic-loop, boltz-tune) remain.

---

## 2026-07-22 (B) — capstone: dbtl-agent

- **B — dbtl-agent built, governance-first** (the idea is crowded; the moat is
  governance). Ties the suite together: guard (hard budget + audit) + binder-triage
  (anti-monoculture selection) + a Thompson-sampling learner over per-family beliefs,
  against a strict simulated oracle.
- Guarantees: budget respected 100%, audit chain valid, no monoculture. Learning:
  +~20-30% binders vs a random baseline at equal budget.
- Suite now: **266 tests, 100% coverage, all green.** Ten tools built — J, K, A, B
  complete; the whole ranked backlog is now built except O, N, M.

---

## 2026-07-22 (K, A) — guard + diversity selection

- **K — foundry-guard**: reservation-based budget guardrails (no call sequence can
  exceed the cap, property-tested), scope allow-list, human escalation, hash-chained
  audit. Introduced shared `adaptyv-core.guard`.
- **A — binder-triage (MVP)**: diversity-aware submodular selection vs naive top-N.
  Honest result: diversity cuts monoculture (identity 0.72 to 0.48, ~1 to ~4.5
  families) for a better worst case — insurance against per-family predictor bias.
- Suite now: **253 tests, 100% coverage, all green.** Nine tools built.

---

## 2026-07-22 (J) — seventh tool: campaign-planner

- **J — campaign-planner built** on the new shared `adaptyv-core.pricing` (plate
  tiers, per-assay prices, publication discount, billing by whole tier).
- Monte-Carlo yield+cost simulation, direct vs two-step sequential strategies,
  budget-aware ranking, and the crossover analysis. Honest result: same expected
  binders; two-step is cheaper only while P(express) < ~50% (and is slower).
- Suite now: **222 tests, 100% coverage, all green.** Seven tools built.

---

## 2026-07-22 (D) — sixth tool: insilico-bench

- **D — insilico-bench built:** a reproducible harness measuring which in-silico
  scores predict wet-lab outcome. numpy metrics (AUC-ROC, average precision,
  Spearman, hit-rate@k) with paired bootstrap CIs; per-score / per-campaign;
  synthetic dataset (declared) + CSV loader for real Proteinbase exports.
- Fixed a real PR-AUC bug (recall-trapezoid → average precision). Demo result on
  synthetic data: ipSAE discriminates (AUC ~0.78) and tracks affinity (rho ~0.9);
  pLDDT ~random — the honest, comparative framing the spec asks for.
- Suite now: **205 tests, 100% coverage, all green.** Six tools built.

---

## 2026-07-22 (docs + H) — per-package docs, then fifth tool

- **Documentation for every package**: added `docs/technical.md` (detailed, English)
  and `docs/vulgarisation.md` (plain-language, French) to all packages, alongside the
  existing README / limitations / JOURNAL.
- **H — sensorgram-triage built:** features (kinetics + cross-replicate K_D
  disagreement), a dependency-free deterministic logistic regression, a synthetic
  labelled set, and the **delegation curve** (auto-approved fraction vs
  false-negative rate) as the central deliverable. Honest: ~60% auto-approved at 0%
  FNR on synthetic labels; a calibratable harness, not a calibrated model.
- Suite now: **189 tests, 100% coverage, all green.** Five tools built.

---

## 2026-07-22 (later) — Fourth tool (L) + expression-rescue (I) deepened

Worked both in one session (requested "en parallèle"):

- **L — adaptyv-pipeline built:** the shared `adaptyv-core.foundry` client
  (Transport protocol, cost-estimate/submit/status/download, webhook HMAC), plus
  the pipeline package — offline `SimulatedBackend` (reuses the kinetics generator),
  real `FoundryBackend`, a persisted/resumable `PipelineStep` with dry-run/budget
  guardrails, JSONL ML-tracker, Typer CLI, and Nextflow + Snakemake templates.
- **I — expression-rescue deepened:** rescue now reports the risk score
  **before→after** (re-diagnosed, so it never assumes the fix helped), honours
  **interface positions** (never mutated), and uses finer substitutions (I/L/V/M→T).
- Suite now: **170 tests, 100% coverage, all green.** Four tools built; the shared
  base gained `biophysics` and `foundry`.

Next: reconcile the real Foundry API shapes; then A/B/K can reuse the client.

---

## 2026-07-22 — Third tool shipped: expression-rescue (spec I)

- Built `adaptyv-core.biophysics` (GRAVY, hydrophobic patches, net charge, pI,
  fractions) and the `expression-rescue` tool: validation (reused from preflight),
  10 positioned developability liabilities, a heuristic risk tier, ≤3-mutation
  rescue, HTML report, Typer CLI (check / estimate / rescue).
- Kept it honest: risk tier is a heuristic, variants are "suggested"; the
  calibrated model + ESM are documented as needing Adaptyv's labelled data.
- Suite now: **139 tests, 100% coverage, all green.** Three tools built, biophysics
  added to the shared base.

Next: spec L (adaptyv-pipeline) or wiring ESM/Proteinbase into I when data lands.

---

## 2026-07-21 (demo prep) — compare feature + Loom scripts

- Added `compare_fits()` + `compare` CLI (independent verifier vs package values),
  an "Independent verification" report section with an honest R_max note, and
  cleaned up `write_zip` (no leftover temp dir). 102 tests, 100% coverage.
- Wrote two finalized, word-for-word Loom scripts in `docs/loom-script.md`:
  **Mix A+C** (finished tool + honesty/tests/security, ~3:45) and **B** (the suite,
  ~5 min). Full command dry-run passes — nothing breaks on camera.

---

## 2026-07-21 (later still) — Test hardening + security + 4 new specs

- **Coverage raised to 100%** (was 90%), 101 tests, `--cov-fail-under=98` enforced
  in `make test` and CI.
- **Security hardening found and fixed by tests:**
  - `DataPackage.from_zip` now guards against path traversal ("zip slip"): any
    member resolving outside the temp dir is rejected. Tests cover `../` and
    absolute-path members.
  - `Settings._token` marked `repr=False` so the Foundry token can never leak into
    logs or tracebacks (a test asserts it).
- Added: config/logging/schemas tests; FASTA edge cases (CRLF, casing, whitespace,
  multichain); validation boundaries + two hypothesis property tests; parser
  error paths; package error paths; fitter edge cases + a hypothesis robustness
  test (fit stays finite, never crashes). Excluded `__main__`/`TYPE_CHECKING`
  guards from coverage.
- **4 new specs integrated into the roadmap** (L, M, N, O; source docs 20–26):
  L `adaptyv-pipeline` ⭐⭐⭐ (Nextflow step — ties with G), O `protviz` (the
  visualisation layer of G/A/H/I/D; kinetics plots are its embryo), N `mosaic-loop`,
  M `boltz-tune` (research). Plans in `docs/action-plans/10`–`13`.

---

## 2026-07-21 (later) — Flagship tool G shipped: adaptyv-kinetics

- Verified the live binding-data-package schema, then built `adaptyv-kinetics`
  end-to-end: parser + synthetic generator, global Langmuir fit with bootstrap CI,
  interpretable QC catalog, self-contained HTML report, Typer CLI.
- Added `stats` (bootstrap) and `report` (HTML) modules to `adaptyv-core`.
- Iterated the fitter/QC against measured recovery error (median-filter split,
  adequate dissociation, split-independent decay metric); documented what stays
  limited in `packages/adaptyv-kinetics/docs/limitations.md`.
- Suite now: **54 tests, mypy --strict clean, ruff clean, 90% coverage.**
- `make demo` now generates a package, QCs it, and renders a report in one go.

Next: spec I (expression-rescue), reusing preflight's validation layer.

---

## 2026-07-21 — Suite bootstrapped: monorepo + core + first tool

**What happened**
1. Studied the 11 project specs and the common-ground doc.
2. Analyzed shared components → decided on one base package (`adaptyv-core`) and
   documented it in `docs/shared-components.md`.
3. Stood up a `uv` workspace monorepo with shared tooling (ruff, mypy --strict,
   pytest, GitHub Actions CI) — ADR in `docs/decisions/0001`.
4. Built `adaptyv-core` foundation (schemas, config, logging, seq I/O + validation).
5. Built `preflight` (spec C) end-to-end — the simplest tool — as proof the chain
   works. All green.
6. Wrote per-project action plans (`docs/action-plans/`) to validate before building.

**Toolchain**
- Python 3.12 (pinned via `.python-version`; host has 3.14 but scientific wheels
  favour 3.12), uv 0.11.

**One-liners to reproduce**
```bash
cd adaptyv-suite
make install      # uv sync --all-packages
make all          # ruff + mypy --strict + pytest (24 tests, 90% cov)
make demo         # preflight on the demo FASTA
```

**Status**
| Package | State |
|---|---|
| adaptyv-core | ✅ foundation (seq I/O + validation); 8 more modules planned |
| preflight | ✅ built & green |
| adaptyv-kinetics (G) | ⏳ next — plan 02 awaiting your validation |
| others | ⏳ planned — see docs/action-plans |

**Notable event:** disk filled up (ENOSPC) mid-build; paused, user freed space,
resumed with no rework.

**Awaiting decision (see docs/action-plans/02):**
- Start adaptyv-kinetics (G) next? (recommended)
- OK to re-verify the binding-data-package schema against the live docs first?
- Should I `git init` + initial commit, or leave version control to you?
