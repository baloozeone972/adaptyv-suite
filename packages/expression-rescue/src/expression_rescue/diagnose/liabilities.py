"""Developability liability catalog.

Rules straight from Adaptyv's "Improve Protein Expression" guide and standard
developability practice. Each liability reports its positions so a correction can
be targeted — that is what separates a useful tool from an opaque score.
"""

from __future__ import annotations

import re

from adaptyv_core.biophysics import fraction, gravy, hydrophobic_patches, isoelectric_point
from adaptyv_core.schemas import Severity

from expression_rescue.schemas import Liability

HIGH_GRAVY_THRESHOLD = 0.4
PI_MIN, PI_MAX = 6.5, 8.0  # minimal solubility window near common buffer pH
HIGH_ALA_THRESHOLD = 0.30
HOMOREPEAT_MIN = 5
RIGID_LINKER_MIN = 11  # residues with no G/S

_N_GLYC = re.compile(r"N[^P][ST]")


def _positions_of(seq: str, residue: str) -> list[int]:
    return [i for i, a in enumerate(seq) if a == residue]


def _dimer_positions(seq: str, dimers: set[str]) -> list[int]:
    return [i for i in range(len(seq) - 1) if seq[i : i + 2] in dimers]


def _unpaired_cys(seq: str) -> list[Liability]:
    cys = _positions_of(seq, "C")
    if len(cys) % 2 == 1:
        return [
            Liability(
                code="UNPAIRED_CYS",
                severity=Severity.WARNING,
                message="Odd number of cysteines: risk of aberrant disulfides",
                positions=cys,
            )
        ]
    return []


def _patches(seq: str) -> list[Liability]:
    out: list[Liability] = []
    for p in hydrophobic_patches(seq, window=7, threshold=2.0):
        out.append(
            Liability(
                code="HYDROPHOBIC_PATCH",
                severity=Severity.WARNING,
                message=f"Hydrophobic patch (mean KD {p.mean_hydropathy:.1f})",
                positions=list(range(p.start, p.end + 1)),
            )
        )
    return out


def _homorepeats(seq: str) -> list[Liability]:
    out: list[Liability] = []
    for match in re.finditer(rf"(.)\1{{{HOMOREPEAT_MIN - 1},}}", seq):
        out.append(
            Liability(
                code="LOW_COMPLEXITY",
                severity=Severity.WARNING,
                message=f"Homorepeat of {match.group(1)!r}",
                positions=list(range(match.start(), match.end())),
            )
        )
    return out


def _rigid_linkers(seq: str) -> list[Liability]:
    out: list[Liability] = []
    for match in re.finditer(rf"[^GS]{{{RIGID_LINKER_MIN},}}", seq):
        out.append(
            Liability(
                code="LONG_RIGID_LINKER",
                severity=Severity.INFO,
                message="Long stretch with no Gly/Ser (rigid linker)",
                positions=list(range(match.start(), match.end())),
            )
        )
    return out


def _global_liabilities(seq: str) -> list[Liability]:
    out: list[Liability] = []
    if gravy(seq) > HIGH_GRAVY_THRESHOLD:
        out.append(
            Liability(
                code="HIGH_GRAVY",
                severity=Severity.WARNING,
                message=f"High overall hydropathy (GRAVY {gravy(seq):.2f})",
            )
        )
    if PI_MIN <= isoelectric_point(seq) <= PI_MAX:
        out.append(
            Liability(
                code="EXTREME_PI",
                severity=Severity.WARNING,
                message=f"pI {isoelectric_point(seq)} near minimal-solubility window",
            )
        )
    if fraction(seq, "A") > HIGH_ALA_THRESHOLD:
        out.append(
            Liability(
                code="HIGH_ALA",
                severity=Severity.INFO,
                message=f"High alanine fraction ({fraction(seq, 'A'):.2f})",
            )
        )
    return out


def _motif_liabilities(seq: str) -> list[Liability]:
    out: list[Liability] = []
    n_glyc = [m.start() for m in _N_GLYC.finditer(seq)]
    if n_glyc:
        out.append(
            Liability(
                code="N_GLYC",
                severity=Severity.INFO,
                message="N-glycosylation sequon N-X-S/T",
                positions=n_glyc,
            )
        )
    if deam := _dimer_positions(seq, {"NG", "NS"}):
        out.append(
            Liability(
                code="DEAMIDATION",
                severity=Severity.INFO,
                message="Deamidation-prone motif (NG/NS)",
                positions=deam,
            )
        )
    if iso := _dimer_positions(seq, {"DG", "DP"}):
        out.append(
            Liability(
                code="ISOMERIZATION",
                severity=Severity.INFO,
                message="Isomerization-prone motif (DG/DP)",
                positions=iso,
            )
        )
    return out


def diagnose(seq: str) -> list[Liability]:
    """Return every developability liability found in a single-chain sequence."""
    return (
        _unpaired_cys(seq)
        + _patches(seq)
        + _homorepeats(seq)
        + _rigid_linkers(seq)
        + _global_liabilities(seq)
        + _motif_liabilities(seq)
    )
