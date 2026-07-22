"""Sequence similarity via k-mer Jaccard — a fast, alignment-free identity proxy."""

from __future__ import annotations


def kmers(seq: str, k: int = 3) -> set[str]:
    """The set of k-mers in a sequence.

    >>> sorted(kmers("ABCD", k=2))
    ['AB', 'BC', 'CD']
    """
    return {seq[i : i + k] for i in range(len(seq) - k + 1)} if len(seq) >= k else {seq}


def identity(a: str, b: str, k: int = 3) -> float:
    """Jaccard similarity of two sequences' k-mer sets, in [0, 1].

    >>> identity("AAAA", "AAAA")
    1.0
    """
    ka, kb = kmers(a, k), kmers(b, k)
    union = ka | kb
    return len(ka & kb) / len(union) if union else 0.0


def max_identity_to_set(seq: str, others: list[str], k: int = 3) -> float:
    """Highest identity of `seq` to any sequence in `others` (0 if empty)."""
    return max((identity(seq, other, k) for other in others), default=0.0)


def mean_pairwise_identity(seqs: list[str], k: int = 3) -> float:
    """Average identity over all unordered pairs — a monoculture indicator."""
    if len(seqs) < 2:
        return 0.0
    total = 0.0
    pairs = 0
    for i in range(len(seqs)):
        for j in range(i + 1, len(seqs)):
            total += identity(seqs[i], seqs[j], k)
            pairs += 1
    return total / pairs
