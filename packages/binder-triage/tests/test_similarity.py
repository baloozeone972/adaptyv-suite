"""Tests for the k-mer similarity helpers."""

from __future__ import annotations

from binder_triage.similarity import identity, kmers, max_identity_to_set, mean_pairwise_identity


def test_kmers() -> None:
    assert kmers("ABCD", k=2) == {"AB", "BC", "CD"}
    assert kmers("AB", k=3) == {"AB"}  # shorter than k


def test_identity_bounds() -> None:
    assert identity("AAAA", "AAAA") == 1.0
    assert identity("AAAAAA", "KKKKKK") == 0.0
    assert 0.0 < identity("ABCDEF", "ABCXEF") < 1.0


def test_identity_empty() -> None:
    assert identity("", "") == 1.0  # two empty sequences are trivially identical


def test_max_identity_to_set() -> None:
    assert max_identity_to_set("AAAA", []) == 0.0
    assert max_identity_to_set("AAAA", ["KKKK", "AAAA"]) == 1.0


def test_mean_pairwise_identity() -> None:
    assert mean_pairwise_identity(["AAAA"]) == 0.0  # needs >= 2
    assert mean_pairwise_identity(["AAAA", "AAAA"]) == 1.0
