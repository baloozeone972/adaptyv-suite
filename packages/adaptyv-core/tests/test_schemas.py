"""Tests for the shared contracts."""

from __future__ import annotations

from adaptyv_core.schemas import (
    AssayType,
    Issue,
    Method,
    PlateTier,
    ProteinDesign,
    Severity,
    Verdict,
)


def test_multichain_split() -> None:
    d = ProteinDesign(name="ab", sequence="EVQ:DIQ")
    assert d.chains == ["EVQ", "DIQ"]
    assert d.residues == "EVQDIQ"


def test_single_chain() -> None:
    d = ProteinDesign(name="x", sequence="ABC")
    assert d.chains == ["ABC"]
    assert d.residues == "ABC"


def test_scores_default_independent() -> None:
    a = ProteinDesign(name="a", sequence="AA")
    b = ProteinDesign(name="b", sequence="BB")
    a.scores["ipsae"] = 1.0
    assert b.scores == {}  # default must not be shared


def test_issue_defaults() -> None:
    i = Issue(code="C", severity=Severity.INFO, message="m")
    assert i.position is None
    assert i.chain is None
    assert i.evidence == {}


def test_enum_values() -> None:
    assert PlateTier.T96.value == 96
    assert Method.BLI.value == "BLI"
    assert AssayType.AFFINITY.value == "affinity"
    assert set(Verdict) == {Verdict.PASS, Verdict.REVIEW, Verdict.REJECT}
