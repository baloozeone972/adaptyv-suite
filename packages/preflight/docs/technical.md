# preflight — technical documentation

A pre-submission linter: catch format and platform errors before a submission
leaves, so they don't cost a paid well or a human-review round.

## Where the logic lives

The rules are `adaptyv_core.seq.validate` (shared — they are also the `validate/`
layer of `expression-rescue`). `preflight` is the report aggregation + CLI on top.

## Rules

| Code | Severity | Rule | Source |
|---|---|---|---|
| `NON_CANONICAL_AA` | critical | residue outside the 20 canonical amino acids | API schema |
| `EMPTY_SEQUENCE` / `LENGTH_OUT_OF_BOUNDS` | critical | length must be 50–700 | Supported Protein Formats |
| `MALFORMED_MULTICHAIN` | critical | empty chain from a stray `:` | API multichain format |
| `NO_AROMATIC_FOR_NANODSF` | critical | Trp/Tyr required for thermostability | Thermostability page |
| `MISSING_TARGET` | critical | screening/affinity need a target | experiment types |
| `INVALID_NAME` | warning | name outside `[A-Za-z0-9._-]` | data-package convention |
| `DUPLICATE_SEQUENCE` | warning | identical sequence submitted twice | paid twice |
| `DUPLICATE_NAME` | critical | names must be unique | data-package convention |
| `PLATE_MISALIGNED` | warning | count not a plate tier (24/48/96/192/384/768) | configurator |

## Verdict logic

Per design: **reject** on any critical, **review** on any warning, else **pass**.
The report is blocking if any design is rejected or any campaign issue is critical;
the CLI exits non-zero in that case, so it gates a design pipeline in CI.

## Data flow

```
FASTA ─▶ parse_fasta ─▶ validate_campaign ─▶ PreflightReport ─▶ text | JSON
                                             (per-design verdicts + campaign issues)
```

## CLI

- `check <fasta> [--assay] [--has-target] [--json]` — exit 1 if blocking.
- `fix <fasta> [--out]` — safe auto-corrections: drop exact duplicates, sanitize names.

## Testing

100% coverage; every rule has a dedicated test, plus CLI exit-code and JSON tests.

## Domain model

Bounded context: **Submission Validation** — a supporting subdomain gating entry
into the whole suite. `ProteinDesign`, `Issue`, `Verdict` are Shared Kernel types
(`adaptyv-core.schemas`); this package adds no new domain concepts, only rules over
them. No relationship to Adaptyv's own Foundry model — validation happens entirely
before an `Experiment` would exist. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md) for how this
context relates to the rest of the suite.
