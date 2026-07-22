"""Rule-based mutation suggestions.

Deliberately conservative and few (max 3 mutations). Variants are NOT
experimentally validated — the report always says "suggested to consider", never
"improved". The tool re-diagnoses each variant, so it reports the before/after
heuristic risk score honestly rather than assuming the change helps. ESM-guided
re-scoring is specified but needs a model; this is the honest rule-based floor.
"""

from __future__ import annotations

from adaptyv_core.schemas import Severity

from expression_rescue.diagnose.liabilities import diagnose
from expression_rescue.schemas import Liability, Variant
from expression_rescue.score.risk import risk_score

MAX_MUTATIONS = 3
_HYDROPHOBIC = set("AILMFWVY")
_SEVERITY_ORDER = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.INFO: 2}

# Conservative replacements chosen to remove the liability while staying polar and
# small (BLOSUM62-informed): branched-aliphatic -> threonine, others -> serine.
_PATCH_REPLACEMENT = {"I": "T", "L": "T", "V": "T", "M": "T"}


def _replacement_for_patch(residue: str) -> str:
    return _PATCH_REPLACEMENT.get(residue, "S")


def _mutation_for(
    seq: list[str], liab: Liability, used: set[int], interface: frozenset[int]
) -> tuple[int, str] | None:
    free = [p for p in liab.positions if p not in used and p not in interface and 0 <= p < len(seq)]
    if liab.code == "UNPAIRED_CYS" and free:
        return free[-1], "S"  # remove the odd cysteine
    if liab.code == "HYDROPHOBIC_PATCH":
        hydrophobic = [p for p in free if seq[p] in _HYDROPHOBIC]
        if hydrophobic:
            pos = hydrophobic[len(hydrophobic) // 2]
            return pos, _replacement_for_patch(seq[pos])
    if liab.code == "DEAMIDATION" and free:
        return free[0], "Q"  # N -> Q breaks the NG/NS motif
    return None


def _prioritized(liabilities: list[Liability]) -> list[Liability]:
    return sorted(liabilities, key=lambda liab: _SEVERITY_ORDER[liab.severity])


def suggest_variants(
    residues: str, liabilities: list[Liability], interface_positions: frozenset[int] = frozenset()
) -> list[Variant]:
    """Suggest one conservative corrected variant (up to MAX_MUTATIONS changes).

    Positions in `interface_positions` are never mutated. The returned variant
    carries the risk score before and after (re-diagnosed), so callers never have
    to assume the correction helped.
    """
    seq = list(residues)
    mutations: list[str] = []
    addressed: list[str] = []
    used: set[int] = set()
    for liab in _prioritized(liabilities):
        if len(mutations) >= MAX_MUTATIONS:
            break
        cand = _mutation_for(seq, liab, used, interface_positions)
        if cand is None:
            continue
        pos, new = cand
        mutations.append(f"{seq[pos]}{pos + 1}{new}")
        addressed.append(liab.code)
        seq[pos] = new
        used.add(pos)
    if not mutations:
        return []
    return [
        Variant(
            sequence="".join(seq),
            mutations=mutations,
            addressed=list(dict.fromkeys(addressed)),
            risk_score_before=risk_score(liabilities),
            risk_score_after=risk_score(diagnose("".join(seq))),
        )
    ]
