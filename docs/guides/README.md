# User guides

Task-oriented guides — "how do I do X?" — for each of the thirteen tools, with real
commands and the output you should expect. For architecture and algorithms, see each
package's `docs/technical.md`; for the one-page pitch, see
[`docs/submission/`](../submission/).

## Install once

```bash
git clone https://github.com/baloozeone972/adaptyv-suite.git
cd adaptyv-suite
make install     # uv sync --all-packages — one venv, every tool, editable
```

Every tool below is then a CLI on your `PATH` inside `uv run` (or activate the venv
directly). All commands work **offline**: they either need no external data (they
generate their own synthetic input) or take a file you already have.

## Guides, by workflow stage

| Stage | Guide |
|---|---|
| Before the lab | [preflight](preflight.md) · [expression-rescue](expression-rescue.md) · [binder-triage](binder-triage.md) |
| Planning spend | [campaign-planner](campaign-planner.md) · [foundry-guard](foundry-guard.md) |
| Running the lab | [adaptyv-pipeline](adaptyv-pipeline.md) · [dbtl-agent](dbtl-agent.md) |
| After the lab | [adaptyv-kinetics](adaptyv-kinetics.md) · [sensorgram-triage](sensorgram-triage.md) |
| Measuring what works | [insilico-bench](insilico-bench.md) · [mosaic-loop](mosaic-loop.md) · [boltz-tune](boltz-tune.md) |
| Shared | [protviz](protviz.md) |

## Conventions used in every guide

- `$` = a shell command you run; the block right after it is the output to expect
  (often trimmed with `…`).
- Every demo is **synthetic and declared** — no tool here needs your real Adaptyv
  data to be useful to read through.
- A non-zero exit code is a feature, not a bug: several CLIs (`preflight check`,
  `adaptyv-kinetics qc --fail-on critical`, `sensorgram-triage triage`) are meant to
  gate a pipeline, so they fail loudly on purpose when something needs attention.
