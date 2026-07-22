"""Minimal, dependency-free FASTA reader/writer.

A tolerant parser is deliberate: submissions arrive from many design tools and
the reader must point at the offending line rather than crash. Heavy parsing
(Biopython) is reserved for biophysics, not for basic ingestion.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from adaptyv_core.schemas import ProteinDesign


class FastaError(ValueError):
    """Raised when a FASTA stream is structurally malformed."""


def parse_fasta(text: str) -> list[ProteinDesign]:
    """Parse FASTA text into designs, preserving order.

    Sequence lines are concatenated and upper-cased; whitespace is stripped.
    The chain separator ':' is kept verbatim.

    >>> parse_fasta(">a\\nEVQL\\n>b\\nDIQ:MTQ")
    [ProteinDesign(name='a', sequence='EVQL', design_method=None, scores={}), \
ProteinDesign(name='b', sequence='DIQ:MTQ', design_method=None, scores={})]
    """
    designs: list[ProteinDesign] = []
    name: str | None = None
    chunks: list[str] = []

    def flush() -> None:
        if name is not None:
            designs.append(ProteinDesign(name=name, sequence="".join(chunks)))

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            flush()
            name = line[1:].strip()
            chunks = []
            if not name:
                raise FastaError(f"Empty header on line {lineno}")
        else:
            if name is None:
                raise FastaError(f"Sequence data before any header on line {lineno}")
            chunks.append(line.upper())
    flush()
    return designs


def read_fasta(path: str | Path) -> list[ProteinDesign]:
    """Read and parse a FASTA file.

    >>> read_fasta("does-not-exist.fasta")  # doctest: +SKIP
    """
    return parse_fasta(Path(path).read_text(encoding="utf-8"))


def _iter_fasta_lines(designs: Iterable[ProteinDesign], width: int) -> Iterator[str]:
    for design in designs:
        yield f">{design.name}"
        seq = design.sequence
        for start in range(0, len(seq), width):
            yield seq[start : start + width]


def write_fasta(designs: Iterable[ProteinDesign], path: str | Path, width: int = 60) -> None:
    """Write designs to a FASTA file, wrapping sequence lines at `width`."""
    lines = "\n".join(_iter_fasta_lines(designs, width))
    Path(path).write_text(lines + "\n", encoding="utf-8")
