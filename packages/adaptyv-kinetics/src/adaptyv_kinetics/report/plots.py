"""Sensorgram plotting — delegates to the shared `protviz` visualisation layer."""

from __future__ import annotations

import numpy as np

from adaptyv_kinetics.models.langmuir import NM_TO_M, response
from adaptyv_kinetics.schemas import KineticFit, Trace
from protviz import Series, sensorgram


def plot_replicate(traces: list[Trace], fit: KineticFit) -> bytes:
    """Plot raw sensorgrams with the fitted model overlaid, as PNG bytes."""
    series: list[Series] = []
    for tr in sorted(traces, key=lambda t: t.concentration_nM):
        t = np.asarray(tr.t, dtype=np.float64)
        y = np.asarray(tr.y, dtype=np.float64)
        t_end = float(t[int(np.argmax(y))])
        model = response(
            t, fit.kon, fit.koff, fit.rmax, tr.concentration_nM * NM_TO_M, t_end, float(np.min(y))
        )
        series.append(Series(t=t, y=y, model=model, label=f"{tr.concentration_nM:g} nM"))
    return sensorgram(series, title=f"{fit.name} rep {fit.replicate} — KD {fit.kd_M * 1e9:.2g} nM")
