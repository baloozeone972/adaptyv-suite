"""Figure primitives for experimentally-validated protein design.

Every function takes plain arrays (not domain objects), so any tool can call them
without a dependency cycle, and returns PNG bytes ready to embed in a report.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from protviz.theme import BASELINE_COLOR, color, new_axes, render

Array = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class Series:
    """One sensorgram: time, response, and an optional fitted model curve."""

    t: Array
    y: Array
    model: Array | None
    label: str


def sensorgram(series: list[Series], title: str = "Sensorgram") -> bytes:
    """Raw binding curves with their fitted models overlaid (dashed)."""
    fig, ax = new_axes()
    for i, s in enumerate(series):
        ax.plot(s.t, s.y, lw=0.9, alpha=0.7, color=color(i), label=s.label)
        if s.model is not None:
            ax.plot(s.t, s.model, lw=1.4, ls="--", color=color(i))
    ax.set_xlabel("time (s)")
    ax.set_ylabel("response (nm)")
    ax.set_title(title)
    ax.legend(fontsize=7, ncol=2)
    return render(fig)


def kinetic_map(kon: Array, koff: Array, labels: list[str] | None = None) -> bytes:
    """k_on vs k_off on log axes, with iso-K_D diagonals (constant k_off/k_on)."""
    fig, ax = new_axes()
    ax.scatter(koff, kon, color=color(0), zorder=3)
    lo = min(float(koff.min()), float(kon.min())) / 10
    hi = max(float(koff.max()), float(kon.max())) * 10
    grid = np.array([lo, hi])
    for kd, name in [(1e-9, "1 nM"), (1e-8, "10 nM"), (1e-7, "100 nM")]:
        ax.plot(grid, grid / kd, ls=":", color=BASELINE_COLOR, lw=0.8)
        ax.text(grid[1], grid[1] / kd, f" K_D {name}", fontsize=6, color=BASELINE_COLOR)
    if labels is not None:
        for x, y, name in zip(koff, kon, labels, strict=True):
            ax.annotate(name, (x, y), fontsize=6, xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("k_off (s^-1)")
    ax.set_ylabel("k_on (M^-1 s^-1)")
    ax.set_title("Kinetic map")
    return render(fig)


def censored_kd(kd_nM: Array, censored: NDArray[np.bool_]) -> bytes:
    """Distribution of measured K_D, with non-binders shown as right-censored."""
    fig, ax = new_axes()
    measured = kd_nM[~censored]
    if measured.size:
        ax.scatter(measured, np.zeros_like(measured), color=color(0), label="measured", zorder=3)
    n_cens = int(censored.sum())
    if n_cens:
        edge = float(kd_nM.max()) * 2 if kd_nM.size else 1.0
        ax.scatter(
            [edge] * n_cens,
            np.zeros(n_cens),
            marker=">",
            color=color(1),
            label=f"non-binder (> LOD), n={n_cens}",
            zorder=3,
        )
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_xlabel("K_D (nM)")
    ax.set_title("K_D distribution (non-binders censored)")
    ax.legend(fontsize=7)
    return render(fig)


def reliability_curve(probs: Array, labels: Array, n_bins: int = 10) -> bytes:
    """Calibration curve: predicted probability vs observed frequency, per bin."""
    fig, ax = new_axes()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    xs, ys = [], []
    for lo, hi in pairwise(edges):
        mask = (probs >= lo) & (probs < hi if hi < 1.0 else probs <= hi)
        if mask.any():
            xs.append(float(probs[mask].mean()))
            ys.append(float(labels[mask].mean()))
    ax.plot([0, 1], [0, 1], ls="--", color=BASELINE_COLOR, label="perfect")
    ax.plot(xs, ys, marker="o", color=color(0), label="model")
    ax.set_xlabel("predicted probability")
    ax.set_ylabel("observed frequency")
    ax.set_title("Reliability (calibration) curve")
    ax.legend(fontsize=7)
    return render(fig)


def hit_rate_at_budget(
    ks: list[int], values: Array, ci_low: Array, ci_high: Array, base_rate: float
) -> bytes:
    """Hit rate vs budget k, with a random baseline — the selection figure."""
    fig, ax = new_axes()
    yerr = np.vstack([values - ci_low, ci_high - values])
    ax.errorbar(ks, values, yerr=yerr, marker="o", capsize=3, color=color(0), label="by score")
    ax.axhline(base_rate, ls="--", color=BASELINE_COLOR, label="random baseline")
    ax.set_xlabel("budget k (top-k by score)")
    ax.set_ylabel("hit rate")
    ax.set_title("Hit rate @ budget")
    ax.legend(fontsize=7)
    return render(fig)
