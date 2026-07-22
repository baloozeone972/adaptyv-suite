"""Aggregate per-design validation into a submission-level report."""

from __future__ import annotations

from adaptyv_core.schemas import AssayType, Issue, ProteinDesign, Severity, Verdict
from adaptyv_core.seq.validate import validate_campaign
from pydantic import BaseModel

_CAMPAIGN_KEY = "__campaign__"


def _verdict(issues: list[Issue]) -> Verdict:
    severities = {i.severity for i in issues}
    if Severity.CRITICAL in severities:
        return Verdict.REJECT
    if Severity.WARNING in severities:
        return Verdict.REVIEW
    return Verdict.PASS


class DesignReport(BaseModel):
    """Per-design verdict and its supporting issues."""

    name: str
    sequence: str
    verdict: Verdict
    issues: list[Issue]


class PreflightReport(BaseModel):
    """Whole-submission result. `blocking` is true when anything must be fixed."""

    assay: AssayType | None
    n_designs: int
    n_reject: int
    n_review: int
    n_pass: int
    campaign_issues: list[Issue]
    designs: list[DesignReport]

    @property
    def blocking(self) -> bool:
        """True if any design is rejected or any campaign issue is critical."""
        campaign_critical = any(i.severity == Severity.CRITICAL for i in self.campaign_issues)
        return self.n_reject > 0 or campaign_critical


def run_preflight(
    designs: list[ProteinDesign],
    assay: AssayType | None = None,
    has_target: bool = False,
) -> PreflightReport:
    """Validate a submission and return a structured report.

    >>> from adaptyv_core.schemas import ProteinDesign
    >>> ok = ProteinDesign(name="d1", sequence="A" * 60 + "W")
    >>> run_preflight([ok]).blocking
    False
    """
    issues_by_name = validate_campaign(designs, assay, has_target)
    campaign_issues = issues_by_name.pop(_CAMPAIGN_KEY, [])

    reports: list[DesignReport] = []
    counts = {Verdict.REJECT: 0, Verdict.REVIEW: 0, Verdict.PASS: 0}
    for design in designs:
        issues = issues_by_name.get(design.name, [])
        verdict = _verdict(issues)
        counts[verdict] += 1
        reports.append(
            DesignReport(name=design.name, sequence=design.sequence, verdict=verdict, issues=issues)
        )

    return PreflightReport(
        assay=assay,
        n_designs=len(designs),
        n_reject=counts[Verdict.REJECT],
        n_review=counts[Verdict.REVIEW],
        n_pass=counts[Verdict.PASS],
        campaign_issues=campaign_issues,
        designs=reports,
    )
