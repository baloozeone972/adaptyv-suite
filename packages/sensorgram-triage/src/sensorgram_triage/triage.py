"""Sort a package's curves into green / orange / red using a trained model."""

from __future__ import annotations

import numpy as np
from adaptyv_kinetics.schemas import Trace

from sensorgram_triage.features import extract
from sensorgram_triage.model import LogisticModel
from sensorgram_triage.schemas import Pile, TriageResult

# Feature-vector indices (see schemas.FEATURE_NAMES).
_SNR, _REL_MAE, _DECAY, _SPIKE, _CONVERGED, _KD_SPREAD = range(6)

ORANGE_AT = 0.30
RED_AT = 0.70


def _reasons(vector: np.ndarray) -> list[str]:
    reasons: list[str] = []
    if vector[_SNR] < 10.0:
        reasons.append("low_snr")
    if vector[_DECAY] < 0.10:
        reasons.append("incomplete_dissociation")
    if vector[_SPIKE] > 6.0:
        reasons.append("spike")
    if vector[_REL_MAE] > 0.15:
        reasons.append("poor_fit")
    if vector[_KD_SPREAD] > 1.0:
        reasons.append("replicate_disagree")
    return reasons


def _pile(prob: float) -> Pile:
    if prob >= RED_AT:
        return Pile.RED
    if prob >= ORANGE_AT:
        return Pile.ORANGE
    return Pile.GREEN


def triage_traces(traces: list[Trace], model: LogisticModel) -> list[TriageResult]:
    """Return a triage decision per replicate, ordered by descending review need."""
    rows = extract(traces)
    if not rows:
        return []
    probs = model.predict_proba(np.vstack([r.vector for r in rows]))
    results = [
        TriageResult(
            name=row.name,
            replicate=row.replicate,
            pile=_pile(float(prob)),
            needs_review_prob=float(prob),
            reasons=_reasons(row.vector),
        )
        for row, prob in zip(rows, probs, strict=True)
    ]
    return sorted(results, key=lambda r: r.needs_review_prob, reverse=True)
