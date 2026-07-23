# adaptyv-pipeline — technical documentation

Make the Adaptyv wet lab a declarative pipeline step: cost dry-run,
resume-after-interruption, ML-tracker logging. The chain of reproducibility now
extends past the lab door.

## Module map

```
schemas.py   StepConfig, RunState, RunStatus
backend.py   LabBackend protocol; SimulatedBackend (offline); FoundryBackend (real)
step.py      PipelineStep: estimate -> guard -> submit -> poll -> fetch, persisted
tracker.py   JSONL record linking model_version -> physical result
cli.py       estimate / run / resume / status
templates/   adaptyv.nf (Nextflow), Snakefile (Snakemake)
```

## State machine

```
PENDING ─▶ ESTIMATED ─▶ (dry-run stops here)
                     ├─▶ BLOCKED            (over budget)
                     └─▶ SUBMITTED ─▶ poll ─┬─▶ DONE     (fetch package)
                                            ├─▶ FAILED
                                            └─▶ (still running) ─▶ resume later
```

`RunState` is written to disk (`<run_id>.state.json` + `.config.json`) after every
transition, so `resume(run_id)` reloads both and re-enters `_advance` from wherever
it stopped. Backends are **stateless** (`fetch_package` takes the config), so the
simulator can regenerate offline and cross-process resume works.

`RunStatus.FAILED` (this pipeline's own domain status, distinct from Foundry's)
is set when the backend reports `ExperimentStatus.CANCELED` — the real API's
closest equivalent to failure; there is no separate `failed` status upstream.

## Guardrails (non-negotiable, property-tested)

1. **Dry-run by default** — nothing is submitted, nothing is spent, without `--execute`.
2. **Estimate before submit** — the cost is always known first.
3. **Budget cap** — over `budget_usd`, the run is `blocked`, never submitted.
4. **Resume never resubmits** — an existing `experiment_id` short-circuits submission.

## Backends

- `SimulatedBackend` — fabricates a schema-conformant package from the requested
  sequences via `adaptyv-kinetics` (deterministic pseudo-affinities). Instant, offline,
  declared synthetic. Its output parses with `adaptyv-kinetics`.
- `FoundryBackend` — wraps `adaptyv_core.foundry.FoundryClient`, wire-compatible
  with the real API (verified against `adaptyv-sdk`'s source). `submit` uses
  `create_experiment(..., auto_confirm=True)` — one call carries the whole
  spend. `fetch_package` follows `list_results()` → `data_package_url`. Webhooks
  are HMAC-SHA256 verified on the raw body. The HTTP transport is
  `# pragma: no cover` (network); all client logic is tested via a fake transport.

## Pipeline integration

`templates/adaptyv.nf` and `templates/Snakefile` call the CLI, dry-run by default,
`--execute` gated behind a config flag, and write a tracker JSONL. The tool is the
**node**, not the DAG engine — Nextflow/Snakemake orchestrate.

## Testing

100% coverage (excluding the network transport). A `StubBackend` with a controllable
poll status exercises the async submitted→resume→done path.

## Domain model

Bounded context: **Pipeline Orchestration** — a **Conformist** sitting directly on
the Foundry Anti-Corruption Layer (`adaptyv_core.foundry`), wrapping it as a
resumable step rather than re-abstracting it. Core aggregates: `StepConfig`,
`RunState`. `RunState`/`RunStatus` are this package's own domain status,
deliberately distinct from (and mapped from) Adaptyv's `ExperimentStatus` — see
the note above on `FAILED`↔`canceled`. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
