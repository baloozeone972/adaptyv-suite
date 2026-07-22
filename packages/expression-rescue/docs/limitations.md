# Known limitations — expression-rescue

Stated explicitly, in the spirit of Adaptyv's own posts.

## The risk score is a heuristic, not a calibrated model

The tier (low/medium/high) is a weighted count of rule-based liabilities. It is
**not** a calibrated P(express). The specified model — LightGBM over liabilities +
biophysical descriptors + ESM-2 log-likelihood, isotonic-calibrated on
Proteinbase expression labels — is not built here because it needs Adaptyv's
labelled data. Calibration matters more than AUC for this use: a client must read
"0.3" as "about three in ten", and that requires their labels.

## Rescue variants are suggestions, not validated

Mutations are conservative and few (max 3), targeting localized liabilities. They
are **not** experimentally validated, and the tool never claims "improved" — only
"suggested to consider". The specified constraints — avoid declared interface
positions, ESM-embedding similarity to preserve predicted function, re-score each
variant — need a model and/or user-supplied interface positions. Validating these
variants is exactly what a run at Adaptyv would settle.

## Scope

- ESM log-likelihood and external solubility predictors (NetSolP/SoluProt) are
  specified but not wired in (heavy deps / offline constraint). The rule-based
  diagnosis degrades gracefully and is useful alone.
- Liabilities run per chain with position offsets, so no motif spans a chain break;
  cross-chain effects (e.g. inter-chain disulfides) are not modelled.
- pI uses EMBOSS pKa values; absolute pI is approximate (±0.5 is normal across
  pKa sets), which is why the rule uses a window, not a hard cutoff.
