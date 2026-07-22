# adaptyv-suite — technical overview

A single technical entry point to the whole suite. Each package also has its own
`docs/technical.md` with the details; this document is the map.

## 1. Shape of the repository

A **uv workspace** (monorepo). One shared foundation package, `adaptyv-core`, holds
the stable primitives; every tool is a thin, focused package on top of it.

```
adaptyv-core ── schemas · seq (io+validate) · biophysics · stats · report ·
                foundry · pricing · guard · config · logging
      ▲
      ├─ preflight            (C)   validation → verdict + CLI
      ├─ adaptyv-kinetics     (G)   package parse · Langmuir fit · QC · report ─┐
      ├─ expression-rescue    (I)   validate + liabilities + risk + rescue      │
      ├─ sensorgram-triage    (H)   ── depends on kinetics ──────────────────────┤
      ├─ insilico-bench       (D)   metrics + bootstrap + report                │
      ├─ campaign-planner     (J)   pricing + Monte-Carlo + ranking             │
      ├─ foundry-guard        (K)   guard + Foundry proxy                       │
      ├─ binder-triage        (A)   similarity + diversity selection ───────────┤
      ├─ dbtl-agent           (B)   guard + binder-triage + oracle + learning ──┘
      ├─ adaptyv-pipeline     (L)   foundry client + backends + resumable step
      ├─ protviz              (O)   shared figures  ◀── adaptyv-kinetics uses it
      ├─ mosaic-loop          (N)   calibration + drift vs Mosaic terms
      └─ boltz-tune           (M)   learning-curve harness
```

Dependency direction is strictly downward (tools → core, and a few tool→tool edges
that never cycle: kinetics→protviz, H→kinetics, B→binder-triage). See
[shared-components.md](shared-components.md).

## 2. Design rules (the same everywhere)

- **Contracts first.** Pydantic v2 models are frozen before any logic, so packages are
  built and tested independently against synthetic fixtures.
- **Small, named, pure.** Functions under 50 lines; no magic constants; side-effecting
  entry points (logging config, network) isolated at the edges.
- **Every number carries its provenance.** Performance metrics ship a bootstrap CI and
  n; every report is stamped with its `DataSource` (synthetic / real / foundry).
- **Offline and deterministic.** All demos run on in-repo synthetic generators; external
  systems (Foundry, Mosaic, Proteinbase, GPU) are behind protocols with fakes.

## 3. The shared base (`adaptyv-core`)

| Module | Purpose |
|---|---|
| `schemas` | frozen enums & models used across tools |
| `seq.io` / `seq.validate` | tolerant FASTA + submission validation rules |
| `biophysics` | GRAVY, hydrophobic patches, net charge, pI (bisection) |
| `stats` | percentile bootstrap CI |
| `report` | self-contained HTML (embeds images as data URIs, source banner) |
| `foundry` | typed API client over a `Transport` protocol + webhook HMAC |
| `pricing` | plate tiers, per-assay prices, publication discount |
| `guard` | reservation-based `Budget`, default-deny `Guard`, hash-chained audit |
| `config` / `logging` | env-only settings (token never logged), structlog JSON |

## 4. How data flows through the tools

- **Before the lab:** `preflight` and `expression-rescue` validate and diagnose designs;
  `binder-triage` and `campaign-planner` decide *what* and *how* to run under a budget;
  `foundry-guard` polices the spend; `dbtl-agent` closes the loop autonomously.
- **Executing:** `adaptyv-pipeline` turns a run into a resumable Nextflow/Snakemake step
  via the `foundry` client (with `SimulatedBackend` for offline runs).
- **After the lab:** `adaptyv-kinetics` re-fits and QCs the returned package;
  `sensorgram-triage` sorts curves and quantifies review saved; `insilico-bench` and
  `boltz-tune` measure what predicts outcome; `mosaic-loop` feeds measurements back into
  the design objective. `protviz` draws them all.

## 5. Quality & security

`make all` = `ruff` (lint+format) + `mypy --strict` + `pytest`. In CI (GitHub Actions):
**285 tests, 100% line coverage, gated at 98%.** Property-based tests (`hypothesis`) on
the FASTA parser, the kinetics fitter, and the budget guardrail. Two real defects were
found *by the tests* and fixed: a zip path-traversal in the package loader, and the
Foundry token leaking into a dataclass `repr`. No secret in code; the token is read from
the environment and never logged.

## 6. Running it

```bash
make install    # uv sync --all-packages
make all        # lint + typecheck + test (what CI runs)
make demo       # synth a package, QC it, render an HTML report
```

Per-tool usage is in each package's `README.md`; what each tool deliberately does **not**
claim is in its `docs/limitations.md`.
