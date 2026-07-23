# Known limitations — adaptyv-pipeline

## Simulated by default

The CLI uses `SimulatedBackend`, which fabricates a package from the requested
sequences (via adaptyv-kinetics) with deterministic pseudo-affinities. It is
**not** a model of real assay outcomes — it exists so the pipeline mechanics
(estimate, guardrails, resume, tracker) run end-to-end offline and are testable.
Every simulated package carries the synthetic-data banner when rendered.

## Real backend not exercised here — and now fact-checked, not just assumed

`FoundryBackend` + `HttpTransport` implement a **simplified** REST shape and need
a token and network, so they are excluded from the test suite (the client logic
is fully tested via a fake transport). Checked against `adaptyvbio/adaptyv-sdk`'s
real source (2026-07): the actual API has a two-step experiment lifecycle
(`create()` then `confirm_quote()`/`submit()`, via a typed `ExperimentsAPI`, not
this repo's single `submit()`), and **results arrive via a `data_package_url`
field on `ResultInfo`** (fetched through `get_results()`), not a direct
`/experiments/{id}/package` endpoint as `download_package()` assumes here. The
fix is a genuine adapter — wrap the real SDK client behind this repo's
`Transport` protocol — not a request-shape tweak. See
[foundry-guard/docs/limitations.md](../../foundry-guard/docs/limitations.md#adaptyv_corefoundry-is-a-simplified-shape-not-the-real-foundry-contract)
for the full comparison.

## Scope

- One step at a time: multi-step DAG orchestration is left to Nextflow/Snakemake,
  which is the point — this tool is the *node*, not the engine.
- Polling is single-shot: `run` polls once and, if the experiment is still
  running, returns `submitted` for a later `resume`. There is no built-in busy
  wait (a real assay takes weeks).
- The ML-tracker writer is JSONL; W&B / MLflow adapters are a thin mapping over the
  same `record()` and are not included.
