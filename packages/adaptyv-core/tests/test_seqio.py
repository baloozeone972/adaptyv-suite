"""Tests for FASTA parsing and writing, including property-based round-trips."""

from __future__ import annotations

import string

import pytest
from adaptyv_core.schemas import ProteinDesign
from adaptyv_core.seq.io import FastaError, parse_fasta, write_fasta
from hypothesis import given
from hypothesis import strategies as st


def test_parse_basic() -> None:
    designs = parse_fasta(">a\nEVQL\n>b\nDIQ:MTQ")
    assert [d.name for d in designs] == ["a", "b"]
    assert designs[1].chains == ["DIQ", "MTQ"]


def test_parse_concatenates_and_uppercases() -> None:
    (design,) = parse_fasta(">x\nevq\nlee")
    assert design.sequence == "EVQLEE"


def test_parse_blank_lines_ignored() -> None:
    assert len(parse_fasta("\n\n>a\nEVQL\n\n")) == 1


def test_sequence_before_header_raises() -> None:
    with pytest.raises(FastaError):
        parse_fasta("EVQL\n>a\nEVQL")


def test_empty_header_raises() -> None:
    with pytest.raises(FastaError):
        parse_fasta(">\nEVQL")


_names = st.text(alphabet=string.ascii_letters + string.digits + "._-", min_size=1, max_size=12)
_seqs = st.text(alphabet="ACDEFGHIKLMNPQRSTVWY", min_size=1, max_size=80)


@given(name=_names, seq=_seqs)
def test_write_read_roundtrip(
    tmp_path_factory: pytest.TempPathFactory, name: str, seq: str
) -> None:
    path = tmp_path_factory.mktemp("fa") / "x.fasta"
    original = [ProteinDesign(name=name, sequence=seq)]
    write_fasta(original, path)
    assert parse_fasta(path.read_text()) == original
