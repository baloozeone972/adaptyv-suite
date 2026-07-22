# preflight — user guide

Catch format and platform mistakes in a submission before they cost a paid well.

## How do I check a FASTA of designs?

```bash
$ uv run preflight check designs.fasta --assay thermostability
```

```
  ! [campaign] PLATE_MISALIGNED: 5 designs do not fill a plate tier; nearest is 24
REVIEW  binder_ok_aromatic
  ! DUPLICATE_SEQUENCE: Identical sequence to dup_of_ok (paid twice)
REJECT  binder_no_aromatic
  ✗ NO_AROMATIC_FOR_NANODSF: Thermostability (nanoDSF) requires at least one Trp or Tyr
REJECT  too_short
  ✗ LENGTH_OUT_OF_BOUNDS: Length 11 outside supported range 50-700
REJECT  has_noncanonical
  ✗ NON_CANONICAL_AA @chain0:24: Non-canonical residue 'B' in chain 0
REVIEW  dup_of_ok
  ! DUPLICATE_SEQUENCE: Identical sequence to binder_ok_aromatic (paid twice)

5 designs — 0 pass, 2 review, 3 reject
```

`✗` is a blocking error (reject), `!` a warning (review). The process **exits non-zero**
whenever anything is blocking, so drop it straight into a CI step to gate a submission.

## How do I check for a specific assay?

Pass `--assay` (`expression` / `screening` / `affinity` / `thermostability`) and, if the
assay needs one, `--has-target`:

```bash
$ uv run preflight check designs.fasta --assay affinity --has-target
```

## How do I get machine-readable output?

```bash
$ uv run preflight check designs.fasta --json
```

Emits the full `PreflightReport` as JSON — pipe it into `jq` or your own tooling.

## How do I auto-fix the safe issues?

```bash
$ uv run preflight fix designs.fasta --out clean.fasta
Wrote 4 designs to clean.fasta (removed 1 duplicates)
```

Drops exact duplicate sequences and sanitises names to `[A-Za-z0-9._-]`. It never touches
anything that needs a judgment call (length, alphabet, target) — those stay as `check`
findings for a human to resolve.

## Gotchas

- `PLATE_MISALIGNED` is a **campaign-level** warning (not tied to one design) — it means
  your count doesn't fill a plate tier (24/48/96/192/384/768), so you're paying for unused
  wells.
- A `DUPLICATE_SEQUENCE` is a warning, not a rejection: it still runs, you just pay twice.

See also: [README](../../packages/preflight/README.md) ·
[technical](../../packages/preflight/docs/technical.md) ·
[limitations](../../packages/preflight/docs/limitations.md).
