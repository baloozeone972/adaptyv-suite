"""Submission validation rules.

Every rule here comes straight from Adaptyv's public documentation (supported
protein formats, experiment types, assay requirements). They are hard
constraints, not heuristics, so they are exhaustively testable and carry no
model. This is the shared foundation of `preflight` and of the `validate/`
layer of `expression-rescue`.
"""

from __future__ import annotations

import re

from adaptyv_core.schemas import AssayType, Issue, PlateTier, ProteinDesign, Severity

CANONICAL_AA: frozenset[str] = frozenset("ACDEFGHIKLMNPQRSTVWY")
MIN_LENGTH = 50
MAX_LENGTH = 700
CHAIN_SEP = ":"
_ASSAYS_REQUIRING_TARGET = frozenset({AssayType.SCREENING, AssayType.AFFINITY})
_AROMATIC_RESIDUES = frozenset("WY")  # intrinsic fluorescence for nanoDSF
_VALID_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
_PLATE_TIERS: frozenset[int] = frozenset(t.value for t in PlateTier)


def _check_alphabet(design: ProteinDesign) -> list[Issue]:
    issues: list[Issue] = []
    for chain_idx, chain in enumerate(design.chains):
        for pos, residue in enumerate(chain):
            if residue not in CANONICAL_AA:
                issues.append(
                    Issue(
                        code="NON_CANONICAL_AA",
                        severity=Severity.CRITICAL,
                        message=f"Non-canonical residue {residue!r} in chain {chain_idx}",
                        chain=chain_idx,
                        position=pos,
                    )
                )
    return issues


def _check_length(design: ProteinDesign) -> list[Issue]:
    n = len(design.residues)
    if n == 0:
        return [
            Issue(code="EMPTY_SEQUENCE", severity=Severity.CRITICAL, message="Sequence is empty")
        ]
    if not MIN_LENGTH <= n <= MAX_LENGTH:
        return [
            Issue(
                code="LENGTH_OUT_OF_BOUNDS",
                severity=Severity.CRITICAL,
                message=f"Length {n} outside supported range {MIN_LENGTH}-{MAX_LENGTH}",
                evidence={"length": float(n)},
            )
        ]
    return []


def _check_chains(design: ProteinDesign) -> list[Issue]:
    if any(chain == "" for chain in design.chains):
        return [
            Issue(
                code="MALFORMED_MULTICHAIN",
                severity=Severity.CRITICAL,
                message=f"Empty chain produced by a stray {CHAIN_SEP!r} separator",
            )
        ]
    return []


def _check_name(design: ProteinDesign) -> list[Issue]:
    if not _VALID_NAME.match(design.name):
        return [
            Issue(
                code="INVALID_NAME",
                severity=Severity.WARNING,
                message=f"Name {design.name!r} has characters outside [A-Za-z0-9._-]",
            )
        ]
    return []


def _check_platform(
    design: ProteinDesign, assay: AssayType | None, has_target: bool
) -> list[Issue]:
    issues: list[Issue] = []
    if assay == AssayType.THERMOSTABILITY and not (set(design.residues) & _AROMATIC_RESIDUES):
        issues.append(
            Issue(
                code="NO_AROMATIC_FOR_NANODSF",
                severity=Severity.CRITICAL,
                message="Thermostability (nanoDSF) requires at least one Trp or Tyr",
            )
        )
    if assay in _ASSAYS_REQUIRING_TARGET and not has_target:
        issues.append(
            Issue(
                code="MISSING_TARGET",
                severity=Severity.CRITICAL,
                message=f"Assay {assay.value!r} requires a target to be specified",
            )
        )
    return issues


def validate_design(
    design: ProteinDesign,
    assay: AssayType | None = None,
    has_target: bool = False,
) -> list[Issue]:
    """Validate a single design's format and platform compatibility.

    >>> from adaptyv_core.schemas import ProteinDesign
    >>> validate_design(ProteinDesign(name="x", sequence="XZ"))[0].code
    'NON_CANONICAL_AA'
    """
    issues = _check_length(design)
    issues += _check_chains(design)
    issues += _check_alphabet(design)
    issues += _check_name(design)
    issues += _check_platform(design, assay, has_target)
    return issues


def _duplicate_issues(designs: list[ProteinDesign]) -> dict[str, list[Issue]]:
    by_seq: dict[str, list[str]] = {}
    by_name: dict[str, int] = {}
    for d in designs:
        by_seq.setdefault(d.residues, []).append(d.name)
        by_name[d.name] = by_name.get(d.name, 0) + 1
    extra: dict[str, list[Issue]] = {}
    for names in by_seq.values():
        if len(names) > 1:
            for name in names:
                others = ", ".join(sorted({n for n in names if n != name}))
                extra.setdefault(name, []).append(
                    Issue(
                        code="DUPLICATE_SEQUENCE",
                        severity=Severity.WARNING,
                        message=f"Identical sequence to {others} (paid twice)",
                    )
                )
    for name, count in by_name.items():
        if count > 1:
            extra.setdefault(name, []).append(
                Issue(
                    code="DUPLICATE_NAME",
                    severity=Severity.CRITICAL,
                    message=f"Name {name!r} used {count} times; names must be unique",
                )
            )
    return extra


def check_plate_alignment(n: int) -> Issue | None:
    """Flag a design count that is not a valid plate tier.

    >>> check_plate_alignment(96) is None
    True
    >>> check_plate_alignment(70).code
    'PLATE_MISALIGNED'
    """
    if n in _PLATE_TIERS:
        return None
    tiers = sorted(_PLATE_TIERS)
    next_tier = next((t for t in tiers if t >= n), tiers[-1])
    return Issue(
        code="PLATE_MISALIGNED",
        severity=Severity.WARNING,
        message=f"{n} designs do not fill a plate tier; nearest is {next_tier}",
        evidence={"count": float(n), "next_tier": float(next_tier)},
    )


def validate_campaign(
    designs: list[ProteinDesign],
    assay: AssayType | None = None,
    has_target: bool = False,
) -> dict[str, list[Issue]]:
    """Validate a whole submission: per-design rules plus cross-design duplicates.

    Returns a mapping from design name to its issues. The synthetic key
    ``"__campaign__"`` carries submission-wide issues (plate alignment).
    """
    result: dict[str, list[Issue]] = {
        d.name: validate_design(d, assay, has_target) for d in designs
    }
    for name, extra in _duplicate_issues(designs).items():
        result.setdefault(name, []).extend(extra)
    plate = check_plate_alignment(len(designs)) if designs else None
    if plate is not None:
        result["__campaign__"] = [plate]
    return result
