# campaign-planner — user guide

Given a budget and success probabilities, rank experiment strategies — including a
**two-step sequential** one (cheap expression filter, then affinity on survivors) the
web configurator can't express.

## How do I plan a campaign?

```bash
$ uv run campaign-planner plan --n 96 --p-express 0.3 --p-bind 0.15 --budget 20000
```

```
two_step_expression_then_affinity $  15,002 [ok]    4.3 binders [1,9]  $3,502/binder
direct_affinity                  $  16,224 [ok]    4.3 binders [1,9]  $3,766/binder

Two-step (expression filter first) is cheaper while P(express) < 50%.
```

Same expected binders (with a 95% CI in brackets), but the two-step strategy is
**cheaper** when expression is unreliable — because it filters out non-expressers
before paying for the expensive affinity assay. Ranking is: within budget first, then
most expected binders, then cheapest.

## How do I know when two-step stops being worth it?

The last line is the answer: it reports the exact P(express) **crossover** above which
direct affinity is cheaper. Raise `--p-express` past that value and `direct_affinity`
moves to the top of the ranking.

## How do I use my own success-probability estimates?

`--p-express` and `--p-bind` are your inputs — plug in an estimate from
`expression-rescue` or `insilico-bench` (or your own model) instead of a guess.

## Using it as a library

```python
from campaign_planner import plan, two_step_crossover, Probs

for r in plan(96, Probs(p_express=0.3, p_bind=0.15), budget=20_000):
    print(r.as_row())
two_step_crossover(96)   # e.g. 0.50
```

## Gotchas

- Costs use `adaptyv-core.pricing`'s **plate-tier billing**: you pay for the whole tier
  you book, not per design — that's exactly why plate alignment and the two-step
  trade-off matter.
- The yield simulation is Monte-Carlo (stochastic for the two-step, since the affinity
  tier size depends on how many designs survive expression) — never a point estimate.

See also: [README](../../packages/campaign-planner/README.md) ·
[technical](../../packages/campaign-planner/docs/technical.md) ·
[limitations](../../packages/campaign-planner/docs/limitations.md).
