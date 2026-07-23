# Known limitations — adaptyv-pipeline

## Simulated by default

The CLI uses `SimulatedBackend`, which fabricates a package from the requested
sequences (via adaptyv-kinetics) with deterministic pseudo-affinities. It is
**not** a model of real assay outcomes — it exists so the pipeline mechanics
(estimate, guardrails, resume, tracker) run end-to-end offline and are testable.
Every simulated package carries the synthetic-data banner when rendered.

## Real backend is now wire-compatible; still needs a live token to exercise

`FoundryBackend` submits via `create_experiment(..., auto_confirm=True)` and
fetches the package by following `ResultInfo.data_package_url` — both matching
`adaptyvbio/adaptyv-sdk`'s real source (verified, 2026-07), not assumed. It
still needs a real token and network to run, so it's excluded from the test
suite the same way `HttpTransport` is (`# pragma: no cover`); every other line
of the client logic (payload shapes, the lifecycle, cost conversion) is tested
via a fake transport shaped exactly like the real API. See
[adaptyv-core/docs/limitations.md](../../adaptyv-core/docs/limitations.md)
for the full comparison and what remains genuinely out of scope (targets,
sequences-as-a-resource, quotes list, feedback, info/health — none of this
suite's tools need them).

## Scope

- One step at a time: multi-step DAG orchestration is left to Nextflow/Snakemake,
  which is the point — this tool is the *node*, not the engine.
- Polling is single-shot: `run` polls once and, if the experiment is still
  running, returns `submitted` for a later `resume`. There is no built-in busy
  wait (a real assay takes weeks).
- The ML-tracker writer is JSONL; W&B / MLflow adapters are a thin mapping over the
  same `record()` and are not included.
