# Known limitations — adaptyv-kinetics

Written explicitly, in the spirit of Adaptyv's own posts (which publish negative
results and confidence intervals).

## Data provenance

- Validated on **synthetic** packages (in-repo generator) and the documented
  schema. Not yet run against a real customer package; the parser is tolerant and
  points at the offending file if the real layout differs. Every generated report
  carries a data-source banner.

## Fitting

- Only the **Langmuir 1:1** model is implemented (global across concentrations,
  per-curve baseline). Mass-transport and bivalent variants are planned (spec
  L3), not built.
- K_D = k_off / k_on is only well determined when the **dissociation window is
  long enough** to show meaningful decay. On exact data recovery is <1%; with
  noise + 3-decimal rounding it stays <15% median when dissociation is adequate,
  and degrades for very slow off-rates. Such cases are flagged
  `INCOMPLETE_DISSOCIATION` rather than reported as a confident number.
- k_on and R_max are mildly correlated; 3-decimal rounding of near-ideal curves
  can shift K_D by a few percent. Realistic noise dominates this in practice.

## QC

- The association/dissociation split is **inferred** (median-filtered peak),
  because the raw CSV schema does not encode it. This is robust to spikes but
  means a rule that needs the exact split — notably **baseline drift** — is not
  reliable and is deliberately not shipped as an active rule; drift instead
  surfaces as `POOR_FIT`. With the run's known split (available internally at
  Adaptyv) a dedicated drift rule becomes reliable.
- Thresholds (`SNR_MIN`, `DECAY_MIN`, `SPIKE_SIGMA_MAX`, `POOR_FIT_REL_MAE`) are
  calibrated on synthetic artifacts. Calibrating them on real labelled curves is
  exactly what an internal dataset at Adaptyv would enable.

## Not in scope

- Image processing; exotic kinetic models beyond bivalent; replacing Adaptyv's
  fitting pipeline. This tool is an independent verifier.
