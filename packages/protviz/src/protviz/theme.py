"""Shared plotting theme: one look across every tool in the suite.

Colour-blind-safe (Okabe-Ito) categorical palette, restrained styling, and a single
`render` helper that turns a figure into PNG bytes for embedding in reports.
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# Okabe-Ito: distinguishable under the common forms of colour blindness.
PALETTE: tuple[str, ...] = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#D55E00",
    "#F0E442",
    "#000000",
)
GRID_COLOR = "#8886"
BASELINE_COLOR = "#8886"
FIGSIZE = (6.2, 3.8)
DPI = 110


def color(i: int) -> str:
    """Cycle through the palette by index."""
    return PALETTE[i % len(PALETTE)]


def new_axes() -> tuple[Figure, Axes]:
    """A themed (figure, axes) pair."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.4)
    ax.set_axisbelow(True)
    return fig, ax


def render(fig: Figure) -> bytes:
    """Tighten, rasterise to PNG bytes, and close the figure."""
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI)
    plt.close(fig)
    return buf.getvalue()
