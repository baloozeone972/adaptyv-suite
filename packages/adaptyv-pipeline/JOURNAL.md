# Journal de bord — adaptyv-pipeline

Logbook with exact commands. Newest entry on top.

---

## 2026-07-22 — Built & green (spec L)

**Goal:** make the wet lab a declarative, reproducible pipeline step. Ties with the
kinetics flagship as the strongest idea — no other CRO can offer it.

**Built:**
- `adaptyv-core.foundry` — the shared Foundry client: `Transport` protocol (so it's
  testable offline), `FoundryClient` (cost-estimate, submit, status, download),
  `verify_webhook` (HMAC-SHA256 on the raw body), `HttpTransport` (urllib, excluded
  from coverage). Used by L now, and by A/B/K later.
- `adaptyv-pipeline`: schemas (StepConfig, RunState, RunStatus); `backend`
  (LabBackend protocol, offline `SimulatedBackend` reusing the kinetics generator,
  real `FoundryBackend`); `step.PipelineStep` (estimate → guard → submit → poll →
  fetch, persisted, resumable); `tracker` (JSONL model-version ↔ result); Typer CLI
  (estimate / run / resume / status); Nextflow + Snakemake templates.

**Commands used:**
```bash
uv sync --all-packages
uv run adaptyv-pipeline estimate designs.fasta --assay affinity
uv run adaptyv-pipeline run designs.fasta --execute --budget 15000 --tracker t.jsonl
uv run adaptyv-pipeline resume <run-id>
make all
```

**Decisions & fixes:**
- `adaptyv-kinetics` had to be added to `[tool.uv.sources]` (it's now a dependency
  of another workspace member, not just the root).
- Backends are **stateless**; `fetch_package` takes the config so the simulator can
  regenerate offline and so cross-process `resume` works (state + config persisted).
- Guardrails proven by tests: dry-run submits nothing, over-budget is blocked,
  estimate always precedes submit, resume never resubmits.
- The real HTTP transport is `# pragma: no cover` (network); all client logic is
  tested through a fake transport.

**Status:** ✅ 170 tests (suite total), 100% coverage, mypy --strict clean, ruff clean.
Offline flow verified: dry-run → estimated $676; over-budget → blocked; execute →
package fetched and parsed by adaptyv-kinetics (20 traces); resume idempotent.

**Next:** reconcile the real Foundry request/response shapes against the live API;
wire the client into triage (A), DBTL (B) and guard (K).
