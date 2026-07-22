# Known limitations — adaptyv-pipeline

## Simulated by default

The CLI uses `SimulatedBackend`, which fabricates a package from the requested
sequences (via adaptyv-kinetics) with deterministic pseudo-affinities. It is
**not** a model of real assay outcomes — it exists so the pipeline mechanics
(estimate, guardrails, resume, tracker) run end-to-end offline and are testable.
Every simulated package carries the synthetic-data banner when rendered.

## Real backend not exercised here

`FoundryBackend` + `HttpTransport` implement the real API calls but need a token
and network, so they are excluded from the test suite (the client logic is fully
tested via a fake transport). The exact request/response shapes should be
reconciled against the live API before production use.

## Scope

- One step at a time: multi-step DAG orchestration is left to Nextflow/Snakemake,
  which is the point — this tool is the *node*, not the engine.
- Polling is single-shot: `run` polls once and, if the experiment is still
  running, returns `submitted` for a later `resume`. There is no built-in busy
  wait (a real assay takes weeks).
- The ML-tracker writer is JSONL; W&B / MLflow adapters are a thin mapping over the
  same `record()` and are not included.
