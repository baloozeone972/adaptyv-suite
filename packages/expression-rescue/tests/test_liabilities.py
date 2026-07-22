"""Tests for the developability liability catalog — one rule at a time."""

from __future__ import annotations

from expression_rescue.diagnose.liabilities import diagnose

CLEAN = "GSDDEE" * 9  # 54 aa, acidic, GS-broken: no liabilities


def _codes(seq: str) -> set[str]:
    return {liability.code for liability in diagnose(seq)}


def test_clean_sequence_has_no_liabilities() -> None:
    assert diagnose(CLEAN) == []


def test_unpaired_cys() -> None:
    assert "UNPAIRED_CYS" in _codes("C" + CLEAN)  # odd cysteines
    assert "UNPAIRED_CYS" not in _codes("CC" + CLEAN)  # even


def test_unpaired_cys_reports_positions() -> None:
    (liab,) = [x for x in diagnose("C" + CLEAN) if x.code == "UNPAIRED_CYS"]
    assert liab.positions == [0]


def test_hydrophobic_patch() -> None:
    liab = [x for x in diagnose("GS" + "I" * 12 + "GS" + CLEAN) if x.code == "HYDROPHOBIC_PATCH"]
    assert liab and liab[0].positions


def test_n_glycosylation_sequon() -> None:
    liab = [x for x in diagnose("NIT" + CLEAN) if x.code == "N_GLYC"]
    assert liab and liab[0].positions == [0]


def test_deamidation_and_isomerization() -> None:
    assert "DEAMIDATION" in _codes("NG" + CLEAN)
    assert "ISOMERIZATION" in _codes("DP" + CLEAN)


def test_high_gravy() -> None:
    assert "HIGH_GRAVY" in _codes("ILVF" * 15)


def test_extreme_pi() -> None:
    # A balanced acid/base sequence lands pI in the [6.5, 8.0] window (pI ~6.9).
    assert "EXTREME_PI" in _codes("GSKKDE" * 9)


def test_high_alanine() -> None:
    assert "HIGH_ALA" in _codes("A" * 30 + "GSDEKR" * 4)


def test_homorepeat_low_complexity() -> None:
    assert "LOW_COMPLEXITY" in _codes("GS" + "Q" * 6 + CLEAN)


def test_rigid_linker() -> None:
    assert "LONG_RIGID_LINKER" in _codes("DEKRDEKRDEKRDE" + CLEAN)  # 14 residues no G/S
