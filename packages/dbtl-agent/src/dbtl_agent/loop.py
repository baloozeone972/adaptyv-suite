"""The autonomous DBTL loop — governance first.

Every round is gated by the shared `guard`: the cost is authorized and reserved
before anything is "submitted", so the campaign can never exceed its budget, and
every round is written to a hash-chained audit journal. Selection is diversity-aware
(anti-monoculture) and learning is Thompson sampling over per-family beliefs.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from adaptyv_core.guard import Budget, Guard, Policy
from adaptyv_core.pricing import price
from adaptyv_core.schemas import AssayType
from binder_triage.schemas import Candidate
from binder_triage.select import diverse_greedy
from binder_triage.similarity import mean_pairwise_identity

from dbtl_agent.belief import ClusterBelief
from dbtl_agent.oracle import SimulatedOracle
from dbtl_agent.schemas import CampaignOutcome, RoundResult


def _select_batch(
    remaining: list[Candidate],
    belief: ClusterBelief,
    rng: np.random.Generator,
    k: int,
    weight: float,
) -> list[Candidate]:
    scored = [
        c.model_copy(update={"p_bind_pred": belief.thompson(c.cluster, rng)}) for c in remaining
    ]
    picked = {c.name for c in diverse_greedy(scored, k, weight)}
    return [c for c in remaining if c.name in picked]


def _learn(belief: ClusterBelief, chosen: list[Candidate], results: dict[str, bool]) -> None:
    counts: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for c in chosen:
        counts[c.cluster][1] += 1
        counts[c.cluster][0] += int(results[c.name])
    for cluster, (binders, total) in counts.items():
        belief.update(cluster, binders, total)


def random_baseline(
    pool: list[Candidate], batch_size: int = 24, max_rounds: int = 6, seed: int = 0
) -> int:
    """Total binders from selecting random batches — the no-learning control."""
    rng = np.random.default_rng(seed)
    oracle = SimulatedOracle(seed)
    remaining = list(pool)
    total = 0
    for _ in range(max_rounds):
        if len(remaining) < batch_size:
            break
        idx = rng.choice(len(remaining), batch_size, replace=False)
        chosen = [remaining[i] for i in idx]
        results = oracle.reveal(chosen)
        total += sum(results.values())
        remaining = [c for c in remaining if c.name not in results]
    return total


def run_campaign(
    pool: list[Candidate],
    policy: Policy,
    batch_size: int = 24,
    max_rounds: int = 6,
    diversity_weight: float = 0.7,
    seed: int = 0,
) -> CampaignOutcome:
    """Run the closed loop until the budget or the rounds or the pool run out."""
    guard = Guard(policy=policy, budget=Budget(policy.max_total_usd))
    oracle = SimulatedOracle(seed)
    belief = ClusterBelief()
    rng = np.random.default_rng(seed + 1)
    remaining = list(pool)
    rounds: list[RoundResult] = []
    total_sub = total_bind = 0
    total_cost = 0.0
    for r in range(max_rounds):
        if not remaining:
            break
        k = min(batch_size, len(remaining))
        cost = price(AssayType.AFFINITY, k).total_usd
        if not guard.authorize(AssayType.AFFINITY, cost).allowed:
            break  # budget/scope guardrail stops the loop; nothing is spent
        reservation = guard.budget.reserve(cost)
        assert reservation is not None  # authorize guaranteed the headroom
        guard.budget.commit(reservation)
        chosen = _select_batch(remaining, belief, rng, k, diversity_weight)
        results = oracle.reveal(chosen)
        n_bind = sum(results.values())
        _learn(belief, chosen, results)
        guard.journal.append("round", {"round": r, "k": k, "binders": n_bind, "cost": cost})
        rounds.append(
            RoundResult(
                round=r,
                n_submitted=k,
                n_binders=n_bind,
                cost_usd=cost,
                hit_rate=round(n_bind / k, 3),
                mean_pairwise_identity=round(
                    mean_pairwise_identity([c.sequence for c in chosen]), 3
                ),
                n_families=len({c.cluster for c in chosen}),
            )
        )
        remaining = [c for c in remaining if c.name not in results]
        total_sub += k
        total_bind += n_bind
        total_cost += cost
    return CampaignOutcome(
        rounds=rounds,
        total_submitted=total_sub,
        total_binders=total_bind,
        total_cost_usd=round(total_cost, 2),
        budget_usd=policy.max_total_usd,
        budget_respected=total_cost <= policy.max_total_usd + 1e-9,
        audit_valid=guard.journal.verify(),
    )
