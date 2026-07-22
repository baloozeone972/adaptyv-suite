"""Tests for the preflight report aggregation and verdict logic."""

from __future__ import annotations

from adaptyv_core.schemas import AssayType, ProteinDesign, Verdict
from preflight.report import run_preflight

_VALID = "A" * 59 + "W"


def test_clean_submission_passes() -> None:
    report = run_preflight([ProteinDesign(name="d1", sequence=_VALID)])
    assert report.n_pass == 1
    assert not report.blocking


def test_reject_on_critical() -> None:
    report = run_preflight(
        [ProteinDesign(name="d1", sequence="A" * 60)], assay=AssayType.THERMOSTABILITY
    )
    assert report.n_reject == 1
    assert report.designs[0].verdict == Verdict.REJECT
    assert report.blocking


def test_review_on_warning_only() -> None:
    two_dups = [ProteinDesign(name=f"d{i}", sequence=_VALID) for i in range(2)]
    report = run_preflight(two_dups)
    assert report.n_review == 2
    assert not report.blocking  # warnings do not block


def test_campaign_plate_issue_surfaced() -> None:
    designs = [ProteinDesign(name=f"d{i}", sequence=_VALID) for i in range(70)]
    report = run_preflight(designs)
    assert any(i.code == "PLATE_MISALIGNED" for i in report.campaign_issues)
