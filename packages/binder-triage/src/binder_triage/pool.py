"""Synthetic candidate pool with design families and a biased predictor.

Designs come in clusters (families of near-identical sequences). Each cluster has a
true binding quality, but the predictor has a **per-cluster systematic bias** — it
is over- or under-confident about whole families. That bias is exactly why naive
top-N (which piles into the single highest-predicted family) can underperform a
diversified selection, and why the TREM2 hackathon saw agents converge to a
monoculture.
"""

from __future__ import annotations

import numpy as np

from binder_triage.schemas import Candidate

_AA = "ACDEFGHIKLMNPQRSTVWY"


def _clamp01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def _base_sequence(rng: np.random.Generator, length: int = 80) -> list[str]:
    return list(rng.choice(list(_AA), size=length))


def _mutate(base: list[str], rng: np.random.Generator, n_mut: int) -> str:
    seq = list(base)
    for pos in rng.choice(len(seq), size=n_mut, replace=False):
        seq[pos] = str(rng.choice(list(_AA)))
    return "".join(seq)


def synthetic_pool(n_clusters: int = 5, per_cluster: int = 40, seed: int = 0) -> list[Candidate]:
    """Generate a clustered pool where the predictor is biased per family.

    Fewer, larger families make the monoculture trap visible: naive top-N piles into
    the single highest-predicted family (high within-family identity), while that
    family may be only mediocre in truth because of the predictor's per-family bias.
    """
    rng = np.random.default_rng(seed)
    candidates: list[Candidate] = []
    for c in range(n_clusters):
        base = _base_sequence(rng)
        true_quality = float(rng.uniform(0.05, 0.6))
        cluster_bias = float(rng.normal(0.0, 0.25))  # the predictor's per-family error
        for i in range(per_cluster):
            p_true = _clamp01(true_quality + float(rng.normal(0, 0.03)))
            p_pred = _clamp01(true_quality + cluster_bias + float(rng.normal(0, 0.04)))
            candidates.append(
                Candidate(
                    name=f"c{c:02d}_d{i:02d}",
                    sequence=_mutate(base, rng, n_mut=2),  # within-family: high identity
                    p_bind_pred=p_pred,
                    p_bind_true=p_true,
                    cluster=c,
                )
            )
    return candidates
