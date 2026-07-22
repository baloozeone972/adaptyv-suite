# dbtl-agent — technical documentation

A governance-first autonomous DBTL loop. It ties the suite together: `guard`
(budget + audit), `binder-triage` (diversity-aware selection), `pricing`.

## Module map

```
schemas.py   RoundResult, CampaignOutcome
oracle.py    SimulatedOracle (strict: only reveals pool designs)
belief.py    ClusterBelief (per-family Beta + Thompson sampling)
loop.py      run_campaign; random_baseline (control)
cli.py       run
```

## One round

```
authorize(cost)  ── denied ─▶ stop (budget/scope guardrail; nothing spent)
     │ allowed
reserve(cost) ▶ commit ──────▶ Thompson-score candidates by family belief
                               ▶ diverse_greedy select k (anti-monoculture)
                               ▶ oracle.reveal → binders
                               ▶ update Beta beliefs per family
                               ▶ append round to hash-chained audit
```

The campaign ends when the budget can't cover another round, the pool is exhausted,
or `max_rounds` is reached.

## The budget guarantee

Cost is authorized **and reserved before submission** via `adaptyv-core.guard`. The
guard's invariant (`spent + reserved ≤ max_total`, property-tested there) means no
sequence of rounds can exceed the budget. `CampaignOutcome.budget_respected` is a
post-hoc check that must always be True.

## Learning: Thompson over families

Each family has a Beta(α, β) posterior over its binding rate (uniform prior). A round
scores every candidate by a *sample* from its family's posterior (`ClusterBelief.thompson`),
then selects a diverse batch. Sampling gives explore-early / exploit-late for free.
Outcomes update the posteriors. Against `random_baseline` (no learning) at equal
budget, the agent captures ~20–30% more binders.

## Anti-monoculture

Selection uses `binder_triage.diverse_greedy`, so even while exploiting good families
the batch keeps `n_families ≥ 3` (tested) — the loop cannot converge to a monoculture,
directly addressing the TREM2 observation.

## Testing

100% coverage. Guarantees: budget never exceeded, tight budget stops early, pool never
re-tested, audit valid. Learning: agent beats random on average over seeds. Diversity:
families maintained. Oracle strictness and determinism covered.
