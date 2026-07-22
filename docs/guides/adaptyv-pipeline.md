# adaptyv-pipeline — user guide

Make the wet lab a declarative, reproducible pipeline step: dry-run cost estimate,
resume across the ~3-week turnaround, and model-version↔result logging.

## How do I get a cost estimate without submitting anything?

```bash
$ uv run adaptyv-pipeline estimate designs.fasta --assay affinity
estimated: dry-run: cost estimated, nothing submitted
```

Nothing is spent — `estimate` always dry-runs.

## How do I actually run it (dry-run by default, opt in to spend)?

```bash
$ uv run adaptyv-pipeline run designs.fasta --assay affinity --budget 15000
run 724d29b6e451 -> estimated: dry-run: cost estimated, nothing submitted
```

Still a dry run — `run` only submits when you pass `--execute` **and** the estimate is
within `--budget`:

```bash
$ uv run adaptyv-pipeline run designs.fasta --assay affinity --budget 15000 --execute
run 76bb13b6a22c -> done: package fetched
```

(Against the offline `SimulatedBackend` used here, submission completes instantly; a
real Foundry run stays `submitted` until the assay finishes, then `resume` picks it up.)

## How do I resume an interrupted run?

Every run gets a `run_id` (printed above) and persists its state to `.adaptyv-runs/`
(gitignored). If the process is killed mid-run — realistic, since a real assay takes
about three weeks — pick it back up:

```bash
$ uv run adaptyv-pipeline resume 76bb13b6a22c
run 76bb13b6a22c -> done: package fetched

$ uv run adaptyv-pipeline status 76bb13b6a22c
run 76bb13b6a22c -> done
  - estimated $676
  - submitted as sim-9420ed13
  - package fetched
```

## How do I link a model version to its physical result?

```bash
$ uv run adaptyv-pipeline run designs.fasta --model-version v3.2 --tracker tracker.jsonl --execute
```

Appends a JSON record (`model_version`, `experiment_type`, `estimate_usd`, `status`,
`package_path`) to `tracker.jsonl` — the join key between your training runs and the
physical outcome they produced.

## How do I use this in Nextflow / Snakemake?

Templates are in `packages/adaptyv-pipeline/src/adaptyv_pipeline/templates/`
(`adaptyv.nf`, `Snakefile`) — both dry-run by default, `--execute` gated behind a config
flag (`params.adaptyv_execute` / `config["adaptyv_execute"]`).

## Gotchas

- **Dry-run is the default everywhere.** Nothing is ever submitted without an explicit
  `--execute`.
- The demo backend (`SimulatedBackend`) fabricates a real, schema-conformant package via
  `adaptyv-kinetics`'s generator — so `resume`/`status` and the rest of the suite can be
  exercised fully offline. A real `FoundryBackend` exists behind the same interface.

See also: [README](../../packages/adaptyv-pipeline/README.md) ·
[technical](../../packages/adaptyv-pipeline/docs/technical.md) ·
[limitations](../../packages/adaptyv-pipeline/docs/limitations.md).
