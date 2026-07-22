# expression-rescue — user guide

Diagnose designs that won't express, and suggest conservative corrected variants — the
workflow Adaptyv's "Improve Protein Expression" guide describes, implemented.

## How do I diagnose a FASTA of designs?

```bash
$ uv run expression-rescue check designs.fasta
```

```
LOW    clean (score 0): clean
HIGH   risky (score 15): UNPAIRED_CYS, HYDROPHOBIC_PATCH, LOW_COMPLEXITY, LONG_RIGID_LINKER,
                         HIGH_GRAVY, HIGH_ALA, DEAMIDATION, ISOMERIZATION

2 sequences — 0 blocked, 1 high-risk
```

Each liability is **positioned** (see the report for exact residue indices), so a fix can
be targeted instead of guessed. A `BLOCK` line means the sequence failed basic validation
(length, alphabet) before diagnosis even ran.

## How do I get an HTML report?

```bash
$ uv run expression-rescue check designs.fasta --report risk.html
```

## How do I estimate the money at risk?

```bash
$ uv run expression-rescue estimate designs.fasta --price-per-protein 169
1 of 2 designs are high-risk, about $169 of a run at $169/protein.
```

## How do I get corrected variants?

```bash
$ uv run expression-rescue rescue designs.fasta --out corrected.fasta
risky: C2S, I8S, N15Q -> risk score 15 to 6 (addresses UNPAIRED_CYS, HYDROPHOBIC_PATCH, DEAMIDATION)
Wrote 1 corrected variants to corrected.fasta
```

Up to 3 conservative mutations. The tool **re-diagnoses** the corrected sequence and
reports the actual risk-score drop — it never assumes the fix helped.

## How do I protect known interface residues from being mutated?

```bash
$ uv run expression-rescue rescue designs.fasta --interface 10,11,45
```

`--interface` takes a comma-separated list of **1-based** positions that `rescue` will
never touch.

## Gotchas

- The risk tier is a **heuristic**, not a calibrated probability — see
  `docs/limitations.md` for what a calibrated model would need (Adaptyv's labelled data).
- Rescue variants are "suggested to consider", never claimed "improved" — only a real
  assay can confirm that.

See also: [README](../../packages/expression-rescue/README.md) ·
[technical](../../packages/expression-rescue/docs/technical.md) ·
[limitations](../../packages/expression-rescue/docs/limitations.md).
