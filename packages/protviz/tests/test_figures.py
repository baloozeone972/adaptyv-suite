"""Tests for the figure primitives. Each must return a valid PNG."""

from __future__ import annotations

import numpy as np

from protviz import (
    Series,
    censored_kd,
    color,
    hit_rate_at_budget,
    kinetic_map,
    new_axes,
    reliability_curve,
    render,
    sensorgram,
)

_PNG = b"\x89PNG\r\n\x1a\n"


def _is_png(b: bytes) -> bool:
    return b[:8] == _PNG and len(b) > 100


def test_sensorgram_with_and_without_model() -> None:
    t = np.linspace(0, 600, 40)
    with_model = Series(t, np.linspace(0, 0.8, 40), np.linspace(0, 0.79, 40), "50 nM")
    without = Series(t, np.linspace(0, 0.4, 40), None, "25 nM")
    assert _is_png(sensorgram([with_model, without]))


def test_kinetic_map_with_and_without_labels() -> None:
    kon = np.array([1e5, 2e5, 5e4])
    koff = np.array([1e-3, 5e-4, 2e-3])
    assert _is_png(kinetic_map(kon, koff))
    assert _is_png(kinetic_map(kon, koff, ["a", "b", "c"]))


def test_censored_kd_variants() -> None:
    kd = np.array([5.0, 12.0, 40.0, 1000.0])
    both = np.array([False, False, False, True])
    assert _is_png(censored_kd(kd, both))
    all_measured = np.array([False, False, False, False])
    assert _is_png(censored_kd(kd, all_measured))
    all_censored = np.array([True, True, True, True])
    assert _is_png(censored_kd(kd, all_censored))


def test_reliability_curve() -> None:
    rng = np.random.default_rng(0)
    probs = rng.random(200)
    labels = (rng.random(200) < probs).astype(float)  # roughly calibrated
    assert _is_png(reliability_curve(probs, labels))


def test_hit_rate_at_budget() -> None:
    ks = [24, 48, 96]
    v = np.array([0.8, 0.6, 0.4])
    assert _is_png(hit_rate_at_budget(ks, v, v - 0.05, v + 0.05, base_rate=0.3))


def test_theme_helpers() -> None:
    assert color(0) == color(len(__import__("protviz").PALETTE))  # cycles
    fig, _ax = new_axes()
    assert _is_png(render(fig))
