# sensorgram-triage — user guide

Auto-sort binding curves into green / orange / red, and quantify **how much human
review can be safely removed** — the central deliverable, not just the sorting.

## How do I see the headline number?

```bash
$ uv run sensorgram-triage calibrate --max-fnr 0.02
Held-out n=20, Brier=0.014. At FNR <= 2%: 60% auto-approved (threshold 0.01).
```

Read this as: *"if you accept being wrong at most 2% of the time, 60% of curves need no
human eye."* `--max-fnr` is the false-negative rate you're willing to accept; the tool
returns the most auto-approving threshold that respects it.

## How do I get the full delegation-curve report?

```bash
$ uv run sensorgram-triage calibrate --max-fnr 0.02 --report delegation.html
```

Opens as a self-contained HTML file with the delegation curve (auto-approved fraction vs
false-negative rate) plotted.

## How do I triage a real package's curves?

```bash
$ uv run sensorgram-triage triage package.zip --report triage.html
```

```
GREEN  clean_a rep1 (p=0.01): clean
RED    nonbinder rep1 (p=0.97): low_snr, poor_fit
REVIEW ...
```

Each line: pile, replicate, the model's `needs_review_prob`, and the interpretable
reasons (low SNR, incomplete dissociation, spike, poor fit, or replicates disagreeing on
K_D) — never a bare score with no explanation.

## Gotchas

- The labels behind `calibrate` are **synthetic** (clean vs artifact-injected curves),
  declared on every report — this is a **calibratable harness**, not a calibrated model.
  Plug in Adaptyv's real review decisions and the same curve becomes the real number.
- `triage` needs a package readable by `adaptyv-kinetics` (`.zip` or a directory).

See also: [README](../../packages/sensorgram-triage/README.md) ·
[technical](../../packages/sensorgram-triage/docs/technical.md) ·
[limitations](../../packages/sensorgram-triage/docs/limitations.md).
