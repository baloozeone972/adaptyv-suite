# Known limitations — dbtl-agent

## This is the crowded idea — governance is the moat

An autonomous DBTL loop is the most-submitted concept for this brief. Shipped bare,
it is undifferentiated. The value here is the **governance layer** (hard budget via
reservation, tamper-evident audit, anti-monoculture selection) — the loop itself is
deliberately simple.

## Simulated oracle, not real KDs

The lab is a strict `SimulatedOracle`: it draws outcomes from each design's generated
`p_bind_true` and only ever answers for designs in the pool. This makes the backtest
honest but is not real data. On a real run the oracle is the Foundry (async, ~3-week
turnaround), gated by `foundry-guard`, with results arriving via webhook.

## Learning lift depends on the data

The ~20–30% lift over random is measured on the synthetic clustered pool with a
per-family signal. On real data the lift is an empirical question and is subject to the
selection-bias caveat noted in `binder-triage`. The **guarantees** (budget, audit,
diversity) do not depend on the data.

## Explore/exploit and diversity are in tension

A higher diversity weight prevents monoculture but caps exploitation (and thus the
hit-rate climb); a lower weight exploits faster but risks concentration. The default
(0.4) is a middle ground, not a tuned optimum. Real deployment would tune this against
the cost of a wasted well vs a missed family.

## Not built (documented extensions)

- Real async execution against the Foundry with webhook ingestion and resume across
  the multi-week turnaround (the pipeline's `PipelineStep` provides the persistence
  pattern).
- A richer surrogate (GP / per-design model) instead of per-family Beta.
- Token attenuation so even a hostile agent can't bypass the proxy (see foundry-guard).
