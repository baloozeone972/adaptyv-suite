# preflight

Pre-submission linter for Adaptyv experiments. Catch format and platform errors
before they cost a paid well or a human-review round.

## Install

```bash
make install    # from repo root — uv sync --all-packages
```

## Use

```bash
# Validate a submission (exit code 1 if blocking)
preflight check designs.fasta --assay affinity --has-target

# Machine-readable output for a pipeline
preflight check designs.fasta --json

# Safe auto-fixes: drop exact duplicates, sanitize names
preflight fix designs.fasta --out clean.fasta
```

## What it checks

- **Format:** canonical 20 AA, length 50–700, multichain `:`, empty chains.
- **Platform:** Trp/Tyr required for thermostability (nanoDSF); target required
  for screening/affinity.
- **Campaign:** duplicate sequence (warning), duplicate name (critical), plate
  tier alignment (24/48/96/192/384/768).

Each design gets a verdict: **pass / review / reject**. The command exits
non-zero when anything is blocking, so it gates a design pipeline in CI.

## Rules live in the shared base

Validation logic is `adaptyv_core.seq.validate` — the same code becomes the
`validate/` layer of `expression-rescue`. preflight is the report + CLI on top.
