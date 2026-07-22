# Contributing

This started as a take-home submission; the workflow below matches the convention
used across Adaptyv's own Python repos (e.g. [`adaptyv-sdk`](https://github.com/adaptyvbio/adaptyv-sdk)),
so it should feel familiar if this is ever merged upstream.

## Setup

```bash
make install          # uv sync --all-packages
pre-commit install    # optional, but matches the CI checks locally
```

## Before opening a PR

```bash
make all              # ruff (lint+format) + mypy --strict + pytest — this is what CI runs
```

The gate: **ruff and mypy --strict clean, and coverage ≥ 98%** (currently 100%). No
exceptions bypass this — if a check fails, fix the underlying issue rather than
suppressing it.

## Conventions

- Python 3.12+, `uv` workspace, `hatchling` build backend.
- Pydantic v2 contracts frozen **before** any logic in a new package.
- Functions under 50 lines; no magic constants; English throughout the code.
- Any reported performance number carries a bootstrap confidence interval and `n`.
- Every report is stamped with its `DataSource` (synthetic / real / foundry) —
  never let a synthetic result look real.
- New packages follow the existing doc set: `README.md`, `docs/technical.md`,
  `docs/vulgarisation.md`, `docs/limitations.md`.

## Env vars

Same names as `adaptyv-sdk`: `ADAPTYV_API_KEY`, `ADAPTYV_API_URL` (optionally
`ADAPTYV_ORGANIZATION_ID`, not yet consumed here). See
[`adaptyv_core.config`](packages/adaptyv-core/src/adaptyv_core/config.py).
