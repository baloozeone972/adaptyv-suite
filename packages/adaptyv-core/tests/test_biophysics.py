"""Tests for biophysical descriptors."""

from __future__ import annotations

from adaptyv_core.biophysics import (
    fraction,
    gravy,
    hydrophobic_patches,
    isoelectric_point,
    net_charge,
)


def test_gravy_hydrophobic_positive() -> None:
    assert gravy("IIVV") > 3.0
    assert gravy("DDEE") < 0.0


def test_gravy_empty() -> None:
    assert gravy("") == 0.0


def test_hydrophobic_patch_found_and_merged() -> None:
    patches = hydrophobic_patches("K" * 5 + "I" * 12 + "K" * 5, window=7)
    assert len(patches) == 1
    assert patches[0].mean_hydropathy > 2.0


def test_no_patch_in_hydrophilic() -> None:
    assert hydrophobic_patches("D" * 30, window=7) == []


def test_short_sequence_no_patch() -> None:
    assert hydrophobic_patches("III", window=7) == []


def test_net_charge_sign() -> None:
    assert net_charge("KKKK", 7.0) > 0
    assert net_charge("DDDD", 7.0) < 0


def test_pi_ordering() -> None:
    assert isoelectric_point("DDDEEE") < isoelectric_point("AAAA") < isoelectric_point("KKKRRR")


def test_pi_is_charge_neutral_point() -> None:
    pi = isoelectric_point("ACDEFGHIKLMNPQRSTVWY")
    assert abs(net_charge("ACDEFGHIKLMNPQRSTVWY", pi)) < 0.05


def test_fraction() -> None:
    assert fraction("AAAG", "A") == 0.75
    assert fraction("", "A") == 0.0
    assert fraction("GSGS", "GS") == 1.0
