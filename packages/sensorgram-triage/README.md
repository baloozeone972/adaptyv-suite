# sensorgram-triage

Adaptyv spends **days 16–21 of its 21-day delivery window** on "Data Review &
Release" — qualified scientists looking at binding curves. This tool auto-sorts
those curves into **green / orange / red** (publishable / review / re-run) and,
more importantly, quantifies **how much of that review can be removed safely**.

Built on `adaptyv-kinetics` (parsing, re-fit, QC). The question it answers is not
"what accuracy does the model reach" but **"how many curves need no human eye, at
a given false-negative rate."**

## Use

```bash
# Train on a synthetic labelled set and print the delegation operating point.
sensorgram-triage calibrate --max-fnr 0.02 --report delegation.html

# Sort a real package's curves into green / orange / red.
sensorgram-triage triage package.zip --report triage.html
```

```python
from sensorgram_triage import calibrate, triage_traces
from adaptyv_kinetics import DataPackage

model, curve = calibrate()
curve.operating_point(0.02)   # e.g. 60% auto-approved at a 0% false-negative rate
triage_traces(DataPackage.from_zip("package.zip").traces(), model)
```

## The central figure

The **delegation curve**: auto-approved fraction vs false-negative rate, over a
held-out split grouped by protein (no leakage). It reads directly as an operating
decision — *"at 2% false negatives, X% of curves are approved automatically, saving
roughly Y scientist-hours per 96-well run."*

## How it works

1. **Features** (per replicate): SNR, fit rel_MAE, dissociation fraction, spike
   score, convergence — plus a protein-level **K_D disagreement across replicates**
   that a per-replicate QC pass (spec G) cannot see.
2. **Model**: a small dependency-free logistic regression (deterministic), trained
   on a synthetic labelled set (clean = good, artifact-injected = needs review).
3. **Delegation**: the auto-approve/FNR trade-off on the held-out split, with a
   Brier score for calibration.

## Honesty

This is a **calibratable harness, not a calibrated model**: the labels are
synthetic (declared). On real data the labels are Adaptyv's own review decisions —
plug them in and the same curve tells you exactly how much review is safe to remove,
and how many labelled curves it would take. See `docs/limitations.md`.
