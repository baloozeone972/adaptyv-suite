"""Biophysical sequence descriptors shared across tools.

Primitives only (hydropathy, patches, charge, pI) — the domain-specific liability
catalog lives in the expression-rescue tool. Reused by expression-rescue (I),
binder-triage (A) and QC (H).

References: Kyte & Doolittle (1982) hydropathy; EMBOSS pKa values for pI.
"""

from __future__ import annotations

from dataclasses import dataclass

# Kyte-Doolittle hydropathy index.
_KD: dict[str, float] = {
    "A": 1.8,
    "R": -4.5,
    "N": -3.5,
    "D": -3.5,
    "C": 2.5,
    "Q": -3.5,
    "E": -3.5,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "L": 3.8,
    "K": -3.9,
    "M": 1.9,
    "F": 2.8,
    "P": -1.6,
    "S": -0.8,
    "T": -0.7,
    "W": -0.9,
    "Y": -1.3,
    "V": 4.2,
}

# EMBOSS pKa values. N/C-term plus ionisable side chains.
_PKA_POS: dict[str, float] = {"K": 10.8, "R": 12.5, "H": 6.5}
_PKA_NEG: dict[str, float] = {"D": 3.9, "E": 4.1, "C": 8.5, "Y": 10.1}
_PKA_NTERM = 8.6
_PKA_CTERM = 3.6


def gravy(seq: str) -> float:
    """Grand average of hydropathy (mean Kyte-Doolittle index).

    >>> round(gravy("IIVV"), 2)
    4.35
    """
    values = [_KD[a] for a in seq if a in _KD]
    return sum(values) / len(values) if values else 0.0


@dataclass(frozen=True, slots=True)
class Patch:
    """A contiguous hydrophobic window."""

    start: int  # 0-based, inclusive
    end: int  # 0-based, inclusive
    mean_hydropathy: float


def hydrophobic_patches(seq: str, window: int = 7, threshold: float = 2.0) -> list[Patch]:
    """Sliding-window hydrophobic patches with mean Kyte-Doolittle above `threshold`.

    Overlapping windows are merged into maximal runs.

    >>> p = hydrophobic_patches("I" * 12, window=7)[0]
    >>> (p.start, p.end)
    (0, 11)
    """
    if len(seq) < window:
        return []
    hits: list[int] = []
    for start in range(len(seq) - window + 1):
        chunk = seq[start : start + window]
        if gravy(chunk) > threshold:
            hits.append(start)
    return _merge_windows(seq, hits, window)


def _merge_windows(seq: str, starts: list[int], window: int) -> list[Patch]:
    patches: list[Patch] = []
    for start in starts:
        end = start + window - 1
        if patches and start <= patches[-1].end + 1:
            prev = patches[-1]
            merged = seq[prev.start : end + 1]
            patches[-1] = Patch(prev.start, end, gravy(merged))
        else:
            patches.append(Patch(start, end, gravy(seq[start : end + 1])))
    return patches


def net_charge(seq: str, ph: float) -> float:
    """Net charge of the peptide at a given pH (Henderson-Hasselbalch).

    >>> net_charge("K", 7.0) > 0
    True
    """
    pos: float = 1.0 / (1.0 + 10.0 ** (ph - _PKA_NTERM))
    pos += sum((1.0 / (1.0 + 10.0 ** (ph - _PKA_POS[a])) for a in seq if a in _PKA_POS), 0.0)
    neg: float = 1.0 / (1.0 + 10.0 ** (_PKA_CTERM - ph))
    neg += sum((1.0 / (1.0 + 10.0 ** (_PKA_NEG[a] - ph)) for a in seq if a in _PKA_NEG), 0.0)
    return pos - neg


def isoelectric_point(seq: str, tol: float = 1e-3) -> float:
    """Isoelectric point via bisection on net charge over pH in [0, 14].

    >>> isoelectric_point("DDDEEE") < 4.0  # acidic sequence
    True
    """
    lo, hi = 0.0, 14.0
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        if net_charge(seq, mid) > 0:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2.0, 2)


def fraction(seq: str, residues: str) -> float:
    """Fraction of the sequence made of any residue in `residues`.

    >>> fraction("AAAG", "A")
    0.75
    """
    if not seq:
        return 0.0
    return sum(1 for a in seq if a in residues) / len(seq)
