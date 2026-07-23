"""Frozen cross-project contracts.

This module is written first and changed rarely. Every package in the suite
depends on these types; individual tools extend them locally but never redefine
the shared enums here. Keeping the contracts in one place is what lets the
projects be built and tested independently against synthetic fixtures.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum

from pydantic import BaseModel, Field


class AssayType(StrEnum):
    """The experiment types Adaptyv offers.

    Matches `adaptyvbio/adaptyv-sdk`'s generated `ExperimentType` enum exactly
    (verified against its source, 2026-07). `EPITOPE_BINNING` and
    `ENZYME_ACTIVITY` have no pricing/turnaround data in `adaptyv_core.pricing`
    yet — using them with `pricing.price()` raises rather than guessing.
    """

    SCREENING = "screening"
    AFFINITY = "affinity"
    EXPRESSION = "expression"
    THERMOSTABILITY = "thermostability"
    FLUORESCENCE = "fluorescence"
    EPITOPE_BINNING = "epitope_binning"
    ENZYME_ACTIVITY = "enzyme_activity"


class Method(StrEnum):
    """Label-free binding measurement methods."""

    BLI = "BLI"
    SPR = "SPR"


class PlateTier(IntEnum):
    """Valid plate sizes. Intermediate values are refused by the lab workflow."""

    T24 = 24
    T48 = 48
    T96 = 96
    T192 = 192
    T384 = 384
    T768 = 768


class Severity(StrEnum):
    """Severity shared by validation issues, QC flags and liabilities."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DataSource(StrEnum):
    """Provenance of any reported number. Always surfaced to the user."""

    REAL = "real"  # Proteinbase or a genuine data package
    SYNTHETIC = "synthetic"  # produced by an in-repo generator
    FOUNDRY = "foundry"  # live API


class ProteinDesign(BaseModel):
    """A single submitted design. Chains are separated by ':' in `sequence`."""

    name: str
    sequence: str
    design_method: str | None = None
    scores: dict[str, float] = Field(default_factory=dict)

    @property
    def chains(self) -> list[str]:
        """Return the individual chain sequences.

        >>> ProteinDesign(name="ab", sequence="EVQ:DIQ").chains
        ['EVQ', 'DIQ']
        """
        return self.sequence.split(":")

    @property
    def residues(self) -> str:
        """The concatenated residues across all chains (separators removed).

        >>> ProteinDesign(name="ab", sequence="EVQ:DIQ").residues
        'EVQDIQ'
        """
        return self.sequence.replace(":", "")


class Issue(BaseModel):
    """A single finding attached to a sequence, at an optional position."""

    code: str
    severity: Severity
    message: str
    chain: int | None = None
    position: int | None = None  # 0-based within the offending chain
    evidence: dict[str, float] = Field(default_factory=dict)


class Verdict(StrEnum):
    """Three-way disposition reused by preflight, QC and triage reports."""

    PASS = "pass"
    REVIEW = "review"
    REJECT = "reject"
