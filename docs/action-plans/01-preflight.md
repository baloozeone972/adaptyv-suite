# Action plan 01 — preflight ✅ DONE

Spec C. Pre-submission linter. Status: **built, all checks green.**

## Problem

Between format mistakes and platform incompatibilities, a submission can waste a
paid well or trigger a human review round (Adaptyv's day 1–7 phase). preflight
catches these before the order leaves.

## Scope delivered

- Format rules: canonical alphabet, length 50–700, multichain `:`, empty chains.
- Platform rules: Trp/Tyr required for thermostability (nanoDSF); target required
  for screening/affinity.
- Campaign rules: duplicate sequence (warning), duplicate name (critical), plate
  tier alignment.
- Three-way verdict (pass / review / reject); non-zero exit code on blocking.
- CLI: `check` (text or `--json`) and `fix` (dedupe + name sanitation).

## Where it lives

- Rules: `adaptyv_core.seq.validate` (shared — reused by expression-rescue).
- Report + CLI: `packages/preflight`.

## Verification

```bash
make all      # ruff + mypy --strict + pytest
make demo     # preflight check on the demo FASTA
```

Result: 24 tests, 90% coverage, mypy strict clean.

## Not done (out of scope, deferred to expression-rescue)

- Biophysical liabilities and expression risk score (needs `adaptyv_core.biophysics`).
- Live cost-estimate call (needs `adaptyv_core.foundry`).
