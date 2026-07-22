"""Edge cases and property-based tests for submission validation."""

from __future__ import annotations

from adaptyv_core.schemas import AssayType, ProteinDesign
from adaptyv_core.seq.validate import (
    CANONICAL_AA,
    MAX_LENGTH,
    MIN_LENGTH,
    check_plate_alignment,
    validate_campaign,
    validate_design,
)
from hypothesis import given
from hypothesis import strategies as st


def _codes(seq: str, **kw: object) -> set[str]:
    return {i.code for i in validate_design(ProteinDesign(name="x", sequence=seq), **kw)}  # type: ignore[arg-type]


def test_length_boundaries_inclusive() -> None:
    assert "LENGTH_OUT_OF_BOUNDS" not in _codes("W" + "A" * (MIN_LENGTH - 1))  # exactly 50
    assert "LENGTH_OUT_OF_BOUNDS" not in _codes("A" * MAX_LENGTH)  # exactly 700
    assert "LENGTH_OUT_OF_BOUNDS" in _codes("A" * (MIN_LENGTH - 1))  # 49
    assert "LENGTH_OUT_OF_BOUNDS" in _codes("A" * (MAX_LENGTH + 1))  # 701


def test_all_canonical_accepted() -> None:
    seq = ("".join(sorted(CANONICAL_AA)) * 3)[:60]
    assert _codes(seq) == set()


def test_lowercase_is_non_canonical() -> None:
    # validate_design works on the residues as stored; the FASTA reader upper-cases.
    assert "NON_CANONICAL_AA" in _codes("a" * 60)


def test_position_reported_in_second_chain() -> None:
    design = ProteinDesign(name="x", sequence="A" * 60 + ":" + "A" * 20 + "Z")
    issues = [i for i in validate_design(design) if i.code == "NON_CANONICAL_AA"]
    assert issues[0].chain == 1
    assert issues[0].position == 20


def test_plate_alignment_above_max_tier() -> None:
    flagged = check_plate_alignment(1000)
    assert flagged is not None
    assert flagged.evidence["next_tier"] == 768


def test_empty_campaign() -> None:
    assert validate_campaign([]) == {}


def test_thermostability_with_tyrosine_ok() -> None:
    assert "NO_AROMATIC_FOR_NANODSF" not in _codes("A" * 59 + "Y", assay=AssayType.THERMOSTABILITY)


@given(seq=st.text(alphabet="".join(sorted(CANONICAL_AA)), min_size=MIN_LENGTH, max_size=200))
def test_property_valid_sequences_have_no_alphabet_error(seq: str) -> None:
    assert "NON_CANONICAL_AA" not in _codes(seq)


@given(seq=st.text(alphabet="BJOUXZ", min_size=1, max_size=50))
def test_property_noncanonical_always_flagged(seq: str) -> None:
    assert "NON_CANONICAL_AA" in _codes(seq)
