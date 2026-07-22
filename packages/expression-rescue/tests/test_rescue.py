"""Tests for rule-based mutation suggestions."""

from __future__ import annotations

from adaptyv_core.schemas import Severity
from expression_rescue.diagnose.liabilities import diagnose
from expression_rescue.rescue.mutations import MAX_MUTATIONS, suggest_variants
from expression_rescue.schemas import Liability
from expression_rescue.score.risk import risk_score


def test_no_addressable_liabilities_yields_nothing() -> None:
    # HIGH_ALA has no targeted mutation rule.
    liab = [Liability(code="HIGH_ALA", severity=Severity.INFO, message="m")]
    assert suggest_variants("A" * 60, liab) == []


def test_unpaired_cys_mutated_to_serine() -> None:
    liab = [Liability(code="UNPAIRED_CYS", severity=Severity.WARNING, message="m", positions=[3])]
    (variant,) = suggest_variants("AAACAAAA", liab)
    assert variant.mutations == ["C4S"]
    assert variant.sequence[3] == "S"
    assert "UNPAIRED_CYS" in variant.addressed


def test_deamidation_n_to_q() -> None:
    liab = [Liability(code="DEAMIDATION", severity=Severity.INFO, message="m", positions=[2])]
    (variant,) = suggest_variants("AANGAA", liab)
    assert variant.mutations == ["N3Q"]


def test_hydrophobic_patch_breaks_with_polar() -> None:
    liab = [
        Liability(
            code="HYDROPHOBIC_PATCH",
            severity=Severity.WARNING,
            message="m",
            positions=list(range(0, 8)),
        )
    ]
    (variant,) = suggest_variants("IIIIIIII", liab)
    assert variant.mutations[0][-1] in "ST"  # replaced with a polar residue


def test_capped_at_max_mutations() -> None:
    liab = [
        Liability(code="UNPAIRED_CYS", severity=Severity.WARNING, message="m", positions=[0]),
        Liability(code="DEAMIDATION", severity=Severity.INFO, message="m", positions=[2]),
        Liability(
            code="HYDROPHOBIC_PATCH", severity=Severity.WARNING, message="m", positions=[4, 5, 6, 7]
        ),
        Liability(code="DEAMIDATION", severity=Severity.INFO, message="m", positions=[9]),
    ]
    (variant,) = suggest_variants("CANGIIIINGAA", liab)
    assert len(variant.mutations) <= MAX_MUTATIONS


def test_variant_reports_before_after_and_lowers_score() -> None:
    # An acidic, GS-broken base (no liabilities) plus an unpaired cys and an NG motif.
    seq = "GSDDEE" * 8 + "C" + "NG" + "GSDDEE"
    liabs = diagnose(seq)
    assert {liability.code for liability in liabs} == {"UNPAIRED_CYS", "DEAMIDATION"}
    (variant,) = suggest_variants(seq, liabs)
    assert variant.risk_score_before == risk_score(liabs)
    assert variant.risk_score_after < variant.risk_score_before
    assert variant.score_delta > 0


def test_interface_positions_are_never_mutated() -> None:
    liab = [Liability(code="UNPAIRED_CYS", severity=Severity.WARNING, message="m", positions=[3])]
    # The only addressable position is protected -> no variant is produced.
    assert suggest_variants("AAACAAAA", liab, interface_positions=frozenset({3})) == []


def test_branched_hydrophobic_replaced_with_threonine() -> None:
    liab = [
        Liability(
            code="HYDROPHOBIC_PATCH",
            severity=Severity.WARNING,
            message="m",
            positions=list(range(8)),
        )
    ]
    (variant,) = suggest_variants("IIIIIIII", liab)
    assert variant.mutations[0].endswith("T")  # I -> T, not the generic S
