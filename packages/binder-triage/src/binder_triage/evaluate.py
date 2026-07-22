"""Turn a chosen subset into a scored Selection, and compare strategies."""

from __future__ import annotations

from adaptyv_core.pricing import plate_tier_for, price
from adaptyv_core.schemas import AssayType

from binder_triage.schemas import Candidate, Selection
from binder_triage.select import diverse_greedy, top_n
from binder_triage.similarity import mean_pairwise_identity


def evaluate(strategy: str, chosen: list[Candidate]) -> Selection:
    """Score a selection: expected binders, true binders (if known), monoculture."""
    seqs = [c.sequence for c in chosen]
    trues = [c.p_bind_true for c in chosen if c.p_bind_true is not None]
    return Selection(
        strategy=strategy,
        names=[c.name for c in chosen],
        plate_tier=plate_tier_for(len(chosen)),
        cost_usd=price(AssayType.AFFINITY, len(chosen)).total_usd,
        expected_binders=round(sum(c.p_bind_pred for c in chosen), 2),
        true_binders=round(sum(trues), 2) if len(trues) == len(chosen) else None,
        mean_pairwise_identity=round(mean_pairwise_identity(seqs), 3),
        n_clusters=len({c.cluster for c in chosen}),
    )


def compare(candidates: list[Candidate], k: int, diversity_weight: float = 0.5) -> list[Selection]:
    """Evaluate top-N and diverse-greedy selections of size k side by side."""
    return [
        evaluate("top_n", top_n(candidates, k)),
        evaluate("diverse_greedy", diverse_greedy(candidates, k, diversity_weight)),
    ]
