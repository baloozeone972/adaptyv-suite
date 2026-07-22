"""Edge cases for the FASTA reader/writer: line endings, casing, whitespace."""

from __future__ import annotations

from pathlib import Path

from adaptyv_core.schemas import ProteinDesign
from adaptyv_core.seq.io import parse_fasta, read_fasta, write_fasta


def test_crlf_line_endings() -> None:
    designs = parse_fasta(">a\r\nEVQL\r\n>b\r\nDIQ")
    assert [d.name for d in designs] == ["a", "b"]
    assert designs[0].sequence == "EVQL"


def test_lowercase_upper_cased() -> None:
    (d,) = parse_fasta(">x\nevqlee")
    assert d.sequence == "EVQLEE"


def test_trailing_and_leading_whitespace() -> None:
    (d,) = parse_fasta("  \n>x\n  EVQL  \n  \n")
    assert d.sequence == "EVQL"


def test_header_with_spaces_kept() -> None:
    (d,) = parse_fasta(">binder 001 desc\nEVQL")
    assert d.name == "binder 001 desc"


def test_empty_text_yields_nothing() -> None:
    assert parse_fasta("") == []
    assert parse_fasta("\n\n\n") == []


def test_multichain_separator_preserved() -> None:
    (d,) = parse_fasta(">x\nHEAVY:LIGHT")
    assert d.chains == ["HEAVY", "LIGHT"]


def test_read_file(tmp_path: Path) -> None:
    p = tmp_path / "x.fasta"
    p.write_text(">a\nEVQL\n")
    assert read_fasta(p)[0].name == "a"


def test_write_wraps_long_sequences(tmp_path: Path) -> None:
    p = tmp_path / "out.fasta"
    write_fasta([ProteinDesign(name="a", sequence="A" * 130)], p, width=60)
    lines = p.read_text().splitlines()
    assert lines[0] == ">a"
    assert max(len(line) for line in lines[1:]) <= 60
    assert parse_fasta(p.read_text())[0].sequence == "A" * 130
