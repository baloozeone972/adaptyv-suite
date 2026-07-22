"""Tests for the submission validation rules — one test per rule."""

from __future__ import annotations

from adaptyv_core.schemas import AssayType, ProteinDesign, Severity
from adaptyv_core.seq.validate import (
    MIN_LENGTH,
    check_plate_alignment,
    validate_campaign,
    validate_design,
)

_VALID = "A" * (MIN_LENGTH - 1) + "W"  # 50 residues, has an aromatic


def _codes(design: ProteinDesign, **kw: object) -> set[str]:
    return {i.code for i in validate_design(design, **kw)}  # type: ignore[arg-type]


def test_valid_design_has_no_issues() -> None:
    assert validate_design(ProteinDesign(name="ok", sequence=_VALID)) == []


def test_non_canonical_flagged_with_position() -> None:
    issues = validate_design(ProteinDesign(name="x", sequence="B" + _VALID[1:]))
    assert issues[0].code == "NON_CANONICAL_AA"
    assert issues[0].position == 0


def test_too_short() -> None:
    assert "LENGTH_OUT_OF_BOUNDS" in _codes(ProteinDesign(name="x", sequence="AWAW"))


def test_empty() -> None:
    assert "EMPTY_SEQUENCE" in _codes(ProteinDesign(name="x", sequence=""))


def test_malformed_multichain() -> None:
    assert "MALFORMED_MULTICHAIN" in _codes(ProteinDesign(name="x", sequence=_VALID + ":"))


def test_invalid_name_is_warning() -> None:
    issues = validate_design(ProteinDesign(name="bad name!", sequence=_VALID))
    assert issues[0].code == "INVALID_NAME"
    assert issues[0].severity == Severity.WARNING


def test_thermostability_requires_aromatic() -> None:
    no_aromatic = ProteinDesign(name="x", sequence="A" * 60)
    codes = _codes(no_aromatic, assay=AssayType.THERMOSTABILITY)
    assert "NO_AROMATIC_FOR_NANODSF" in codes


def test_affinity_requires_target() -> None:
    design = ProteinDesign(name="x", sequence=_VALID)
    assert "MISSING_TARGET" in _codes(design, assay=AssayType.AFFINITY, has_target=False)
    assert "MISSING_TARGET" not in _codes(design, assay=AssayType.AFFINITY, has_target=True)


def test_duplicate_sequence_and_name() -> None:
    designs = [
        ProteinDesign(name="a", sequence=_VALID),
        ProteinDesign(name="a", sequence=_VALID),
    ]
    result = validate_campaign(designs)
    codes = {i.code for issues in result.values() for i in issues}
    assert {"DUPLICATE_SEQUENCE", "DUPLICATE_NAME"} <= codes


def test_plate_alignment() -> None:
    assert check_plate_alignment(96) is None
    misaligned = check_plate_alignment(70)
    assert misaligned is not None
    assert misaligned.evidence["next_tier"] == 96
