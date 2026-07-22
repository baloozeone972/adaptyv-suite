# adaptyv-pipeline

A protein-design pipeline is reproducible **up to the lab door** and no further:
you export a FASTA, open a web portal, wait three weeks, download a ZIP, and paste
results back by hand. This tool makes the Adaptyv wet lab a **declarative pipeline
step** — with a cost dry-run, resume-after-interruption, and automatic ML-tracker
logging that ties a model version to the physical result it produced.

No other CRO can offer this, because no other CRO has an API.

## Use

```bash
# Dry-run cost estimate — never submits.
adaptyv-pipeline estimate designs.fasta --assay affinity

# Estimate, then (only with --execute and within budget) submit, poll, fetch.
adaptyv-pipeline run designs.fasta --assay affinity --execute --budget 15000 \
    --model-version v3 --tracker runs.jsonl

# A real assay takes ~3 weeks; a run persists and resumes exactly where it stopped.
adaptyv-pipeline resume <run-id>
adaptyv-pipeline status <run-id>
```

```python
from adaptyv_pipeline import PipelineStep, SimulatedBackend, StepConfig
from adaptyv_core.schemas import AssayType

step = PipelineStep(SimulatedBackend(), ".runs")
state = step.run(StepConfig(experiment_type=AssayType.AFFINITY,
                            sequences={"d1": "MK..."}, dry_run=False, budget_usd=15000))
state.status        # done ; state.package_path parses with adaptyv-kinetics
```

## Guardrails (non-negotiable)

- **Dry-run by default:** nothing is submitted — nothing is spent — without an
  explicit `--execute`.
- **Estimate before submit:** the cost is always known first; over `--budget` the
  run is `blocked`, never submitted.
- **Deterministic resume:** state is persisted after every transition.

## Backends

- `SimulatedBackend` (default in the CLI) — fabricates a schema-conformant package
  from the requested sequences via `adaptyv-kinetics`, so the whole flow runs
  offline and reproducibly. **Declared as simulated.**
- `FoundryBackend` — the real lab via `adaptyv_core.foundry.FoundryClient` (needs a
  token). Webhook signatures are HMAC-SHA256 verified on the raw body.

## Pipeline templates

`src/adaptyv_pipeline/templates/` ships a Nextflow module (`adaptyv.nf`) and a
Snakemake rule (`Snakefile`) that call the CLI — dry-run by default, `--execute`
gated behind a config flag.
