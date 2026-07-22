# adaptyv-suite

Internal tooling for Adaptyv Bio's protein-engineering workflows — a monorepo of
small, **finished** tools built on one shared foundation.

> 🎥 **Loom walkthrough:** _<add your Loom link here>_

Adaptyv ships every binding customer a data package of raw sensorgrams, fitted
curves and QC metrics — and no tool to read it. It publishes a protein-expression
workflow nobody has implemented, and spends a quarter of its delivery window on
manual data review. Every tool here targets a **friction documented in Adaptyv's
own material**, not a guessed one.

The guiding principle: a small finished tool beats a large unfinished one. So the
suite ships one polished flagship, one tiny utility, and a shared base — plus a
prioritised plan for the rest.

## What's here now

| Package | What it does | Status |
|---|---|---|
| [`adaptyv-core`](packages/adaptyv-core) | Shared base: frozen data contracts, sequence I/O + validation, biophysics, bootstrap statistics, self-contained HTML reporting, config/logging | ✅ built |
| [`adaptyv-kinetics`](packages/adaptyv-kinetics) | **Flagship.** Reads the binding data package, re-fits kinetics independently, flags artifacts, and renders a report — in one command | ✅ built |
| [`adaptyv-pipeline`](packages/adaptyv-pipeline) | Make the wet lab a declarative, reproducible pipeline step (Nextflow/Snakemake): cost dry-run, resume, ML-tracker logging | ✅ built |
| [`sensorgram-triage`](packages/sensorgram-triage) | Auto-sort binding curves (green/orange/red) and quantify how much human review can be safely removed | ✅ built |
| [`insilico-bench`](packages/insilico-bench) | Measure which in-silico scores (ipSAE, ipTM, pLDDT…) actually predict wet-lab outcome — a reproducible harness | ✅ built |
| [`campaign-planner`](packages/campaign-planner) | Enumerate and rank experiment strategies under a budget, including two-step sequential ones | ✅ built |
| [`foundry-guard`](packages/foundry-guard) | Guardrail proxy over the Foundry API: spend caps, scope allow-lists, human escalation, hash-chained audit | ✅ built |
| [`binder-triage`](packages/binder-triage) | Diversity-aware selection of designs under a plate budget — avoids the top-N monoculture trap | ✅ built (MVP) |
| [`dbtl-agent`](packages/dbtl-agent) | Governance-first autonomous DBTL loop: hard budget, tamper-evident audit, anti-monoculture, learning | ✅ built |
| [`protviz`](packages/protviz) | Shared visualisation layer (sensorgrams, kinetic maps, censored KD, calibration) — used by adaptyv-kinetics | ✅ built |
| [`mosaic-loop`](packages/mosaic-loop) | Recalibrate Mosaic's objective terms with Adaptyv measurements; flag which predicted terms drift from reality | ✅ built |
| [`boltz-tune`](packages/boltz-tune) | Learning-curve harness: does affinity fine-tuning help, and how much data would a real gain need | ✅ built (harness) |
| [`expression-rescue`](packages/expression-rescue) | Diagnose designs that won't express and suggest corrected variants — the workflow Adaptyv published, implemented | ✅ built |
| [`preflight`](packages/preflight) | Pre-submission linter: catch format/platform errors before they cost a paid well | ✅ built |

**Every specced tool is now built** — see the [roadmap](docs/action-plans/00-roadmap.md).

## 60-second demo

```bash
make install                                  # uv sync --all-packages

# No real package handy? Generate a schema-conformant synthetic one.
adaptyv-kinetics synth --out package.zip

# One command: parse, re-fit, QC, and render a self-contained HTML report.
adaptyv-kinetics report package.zip -o report.html

# The independent-verifier view: re-fit vs the package's reported values.
adaptyv-kinetics compare package.zip

# QC verdicts; non-zero exit on any reject (usable in CI).
adaptyv-kinetics qc package.zip --fail-on critical
```

```python
from adaptyv_kinetics import DataPackage

pkg = DataPackage.from_zip("package.zip")   # or .from_dir("package/")
pkg.summary()                 # name, replicate, method, MAE, rel_MAE, Rmax
pkg.refit(bootstrap=1000)     # independent kon/koff/KD + bootstrap CI
pkg.qc()                      # per-replicate verdict: pass / review / reject
pkg.report("report.html")     # self-contained HTML
```

## Architecture — one shared base

The suite is a `uv` workspace. Every tool depends on a single package,
`adaptyv-core`, which holds the stable primitives (contracts, sequence handling,
statistics, reporting). Pydantic contracts are **frozen first** so each tool can
be built and tested independently against synthetic fixtures. See
[docs/shared-components.md](docs/shared-components.md) and
[ADR 0001](docs/decisions/0001-monorepo-uv-workspace.md).

```
packages/
  adaptyv-core/       shared base (schemas, seq, biophysics, stats, report, foundry, pricing, guard, config)
  adaptyv-kinetics/   binding data-package toolkit  (flagship, spec G)
  adaptyv-pipeline/   wet lab as a reproducible pipeline step (spec L)
  sensorgram-triage/  auto-sort curves + delegation analysis (spec H)
  insilico-bench/     which in-silico score predicts wet-lab outcome (spec D)
  campaign-planner/   budget-aware strategy planner (spec J)
  foundry-guard/      guardrail proxy over the Foundry API (spec K)
  binder-triage/      diversity-aware selection under a plate budget (spec A)
  dbtl-agent/         governance-first autonomous DBTL loop (spec B)
  protviz/            shared visualisation layer (spec O)
  mosaic-loop/        recalibrate Mosaic's objective with measurements (spec N)
  boltz-tune/         learning-curve harness for fine-tuning (spec M)
  expression-rescue/  developability diagnosis + rescue (spec I)
  preflight/          pre-submission linter          (spec C)
docs/
  shared-components.md   which components are shared, and why there is one base
  action-plans/          per-project plans (00-roadmap.md is the index)
  decisions/             architecture decision records (ADR)
  loom-script.md         the video scripts
```

Every package carries the same documentation set:

- `README.md` — how to use it;
- `docs/technical.md` — detailed technical reference (architecture, algorithms, data flow);
- `docs/vulgarisation.md` — a plain-language explanation (in French) for a general audience;
- `docs/limitations.md` — what it deliberately does not claim (where applicable);
- `JOURNAL.md` — a build logbook with the exact commands run, so the work can be
  followed and reproduced step by step.

## Quality & security

```bash
make all     # ruff + mypy --strict + pytest (this is what CI runs)
```

- **285 tests, 100% line coverage**, gated at 98% in CI.
- `ruff` (lint + format) and `mypy --strict` clean across all packages.
- Property-based tests (`hypothesis`) on the parsers and the fitter.
- Two real issues were found **by the tests** and fixed: a zip path-traversal
  ("zip slip") in the package loader, and the Foundry token leaking into a
  dataclass `repr`. Both are regression-tested.
- No secret in code: the Foundry token is read from the environment, never logged.

## Data & honesty

Everything in the demo runs on **synthetic data generated in-repo** — and it is
declared on every report, in the CLI, and in the Loom — because a candidate has no
real customer package. The synthetic generator doubles as the validation harness:
the true parameters are known, so the fitter's recovery error is measured
(exact data <1%; realistic noise <15% median when dissociation is adequate).

What the tools deliberately **do not** claim is written down —
see [adaptyv-kinetics/docs/limitations.md](packages/adaptyv-kinetics/docs/limitations.md):
R_max needs saturation, drift detection needs the run's known association/
dissociation split, and QC thresholds need real labelled curves to be calibrated.
That honesty mirrors Adaptyv's own posts, which publish confidence intervals and
negative results.

## Roadmap

Simplest first, then by the ranking from the specs. Two later ideas are as strong
as the flagship: **adaptyv-pipeline (L)** — making the wet lab a reproducible
Nextflow step, which no other CRO can offer because none has an API — and
**protviz (O)**, the visualisation layer these tools already share. Full plan and
the four newest specs (L, M, N, O) in
[docs/action-plans/00-roadmap.md](docs/action-plans/00-roadmap.md).

## Ground rules

- Python 3.12+, `uv` workspace, Pydantic v2 contracts frozen first.
- Any reported number carries its data source and, where it's a performance
  metric, a confidence interval and sample size.
- English throughout the code; functions under 50 lines; no magic constants.
