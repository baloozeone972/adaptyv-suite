# Known limitations — binder-triage

## Selection bias (the caveat that matters on real data)

Published designs have usually already passed an in-silico filter, so any model
trained or evaluated on them learns "binds | passed the filter", not "binds". On real
Proteinbase data the predicted probabilities are optimistic for this reason. The tool's
value — diversity-aware selection — is unaffected (it operates on whatever scores you
give it), but the absolute yield numbers must be read with this bias in mind.

## The predictor is an input, not built here

The MVP consumes a `p_bind_pred` per candidate; it does not train the binding model.
The real model (LightGBM + biophysics + ESM log-likelihood, calibrated on Proteinbase,
with grouped cross-validation by sequence cluster **and** campaign) is specified but
needs Adaptyv's data. `expression-rescue` and `insilico-bench` supply pieces of it.

## Diversity result is honest, not a free lunch

On the synthetic pool, diversity trades a small amount of *predicted* yield for a much
less monoculture selection and a **better worst case** — insurance against per-family
predictor bias, not a guaranteed increase in mean binders. The magnitude depends on how
biased the predictor actually is per family; on real data that is an empirical question.

## Scope

- Identity uses k-mer Jaccard (fast, alignment-free). Structure- or embedding-based
  diversity would be more faithful and slots into the same objective.
- Selection is submodular greedy. DPP and ILP variants (specced) can improve the
  diversity/coverage trade-off at higher cost.
- No expression-aware two-stage selection yet (that is campaign-planner's territory).
