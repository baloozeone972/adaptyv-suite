# Known limitations — sensorgram-triage

## A calibratable harness, not a calibrated model

The labels are **synthetic** (clean binders vs artifact-injected / non-binders),
generated in-repo and declared on every report. The delegation curve is therefore
measured against known synthetic truth. On real data the labels are Adaptyv's own
review decisions; plugging them in is what turns this harness into a calibrated
model. The learning-curve question — how many labelled curves suffice — is the
natural next measurement.

## Synthetic separability

Artifacts (non-binder, incomplete dissociation, spike) are easy to separate, which
would make the curve trivial. To keep it realistic, good binders span a range of
measurement noise so the noisiest ones overlap the problematic ones. This is a
modelling choice, not a property of real data; real overlap comes from genuinely
ambiguous curves.

## Scope

- The model is a small logistic regression by design (interpretable, deterministic,
  no heavy dependency). A gradient-boosted model would likely rank slightly better
  on real data; the harness swaps it out without changing the delegation analysis.
- Triage is per replicate; the cross-replicate disagreement feature is shared across
  a protein's replicates. Inter-plate drift over a client's history is not modelled.
- The review UI (Streamlit) from the spec is not included; the CLI + HTML report
  cover the demonstration and the operating decision.
