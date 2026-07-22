# ADR 0001 — Monorepo on a uv workspace with a shared core

Status: accepted · 2026-07-21

## Context

The specs describe 11 tools that share a lot of surface (sequence handling,
validation, statistics, Foundry client, reporting). Building them as isolated
repos would duplicate that surface and let the contracts drift apart.

## Decision

One repository, a `uv` workspace with members under `packages/*`, and a single
shared package `adaptyv-core` that every tool depends on.

- Root `pyproject.toml` is a virtual root (`package = false`) carrying the dev
  toolchain and the tool config (ruff, mypy, pytest) so every package obeys the
  same rules.
- Runtime deps live in each member; the shared base is `adaptyv-core`
  (`{ workspace = true }`).
- `uv sync --all-packages` installs the whole suite editable in one venv.

## Consequences

- **Positive:** one lint/type/test config; contracts frozen once in
  `adaptyv_core.schemas`; a tool can reuse another's building blocks without a
  release dance; a new project starts by adding a folder under `packages/`.
- **Cost:** `uv sync` alone only installs the root; the suite needs
  `--all-packages` (encoded in `make install` and CI).
- **Type checking:** mypy needs `mypy_path` set to each `src` root to avoid the
  "source file found twice" ambiguity of the src layout.

## Alternatives considered

- One flat package with sub-modules — rejected: the tools have different runtime
  dependencies (ESM, LightGBM, FastAPI) and should install independently.
- Separate repos + a published `adaptyv-core` — rejected: too much release
  overhead for a take-home-scale suite; drift risk.
