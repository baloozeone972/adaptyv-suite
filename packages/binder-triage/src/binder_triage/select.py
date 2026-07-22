"""Selection strategies: naive top-N vs a diversity-aware submodular greedy."""

from __future__ import annotations

from binder_triage.schemas import Candidate
from binder_triage.similarity import max_identity_to_set


def top_n(candidates: list[Candidate], k: int) -> list[Candidate]:
    """Pick the k designs with the highest predicted P(binds). The naive baseline."""
    return sorted(candidates, key=lambda c: c.p_bind_pred, reverse=True)[:k]


def diverse_greedy(
    candidates: list[Candidate], k: int, diversity_weight: float = 0.5
) -> list[Candidate]:
    """Greedily pick designs maximising predicted binding minus a redundancy penalty.

    Marginal gain of a candidate = `p_bind_pred - diversity_weight * max identity to
    the already-selected set`. This is a classic submodular objective; greedy gives a
    (1 - 1/e) guarantee and, crucially, stops the selection collapsing into one family.
    """
    selected: list[Candidate] = []
    remaining = list(candidates)
    while remaining and len(selected) < k:
        chosen_seqs = [c.sequence for c in selected]
        best = max(
            remaining,
            key=lambda c: (
                c.p_bind_pred - diversity_weight * max_identity_to_set(c.sequence, chosen_seqs)
            ),
        )
        selected.append(best)
        remaining.remove(best)
    return selected
