"""Global Langmuir fitting across concentrations, with a bootstrap CI on K_D.

k_on, k_off and R_max are shared across all concentrations of one replicate; a
baseline offset is free per curve. Optimisation is Trust Region Reflective with
positivity enforced via log-scaling of the rate constants.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

from adaptyv_kinetics.models.langmuir import NM_TO_M, infer_assoc_end, response
from adaptyv_kinetics.schemas import KineticFit, Trace


@dataclass(frozen=True, slots=True)
class _Curve:
    t: NDArray[np.float64]
    y: NDArray[np.float64]
    conc_M: float
    t_assoc_end: float


def _to_curves(traces: list[Trace]) -> list[_Curve]:
    curves: list[_Curve] = []
    for tr in traces:
        t = np.asarray(tr.t, dtype=np.float64)
        y = np.asarray(tr.y, dtype=np.float64)
        curves.append(_Curve(t, y, tr.concentration_nM * NM_TO_M, infer_assoc_end(t, y)))
    return curves


def _predict(params: NDArray[np.float64], curves: list[_Curve]) -> list[NDArray[np.float64]]:
    kon = 10.0 ** params[0]
    koff = 10.0 ** params[1]
    rmax = params[2]
    return [
        response(c.t, kon, koff, rmax, c.conc_M, c.t_assoc_end, baseline=params[3 + i])
        for i, c in enumerate(curves)
    ]


def _residuals(params: NDArray[np.float64], curves: list[_Curve]) -> NDArray[np.float64]:
    preds = _predict(params, curves)
    return np.concatenate([pred - c.y for pred, c in zip(preds, curves, strict=True)])


def _initial(curves: list[_Curve]) -> tuple[NDArray[np.float64], list[tuple[float, float]]]:
    rmax0 = max(float(np.max(c.y)) for c in curves)
    params = [5.0, -3.0, rmax0] + [float(np.min(c.y)) for c in curves]
    bounds_lo = [2.0, -5.0, 0.0] + [-rmax0 for _ in curves]
    bounds_hi = [8.0, 0.0, 5.0 * rmax0 + 1e-9] + [rmax0 for _ in curves]
    return np.array(params, dtype=np.float64), list(zip(bounds_lo, bounds_hi, strict=True))


def _solve(curves: list[_Curve], p0: NDArray[np.float64], bounds: list[tuple[float, float]]):  # type: ignore[no-untyped-def]
    lo = np.array([b[0] for b in bounds])
    hi = np.array([b[1] for b in bounds])
    # Keep the initial guess strictly inside the box; a noisy baseline estimate
    # can otherwise fall on or past a bound (e.g. for non-binders) and scipy raises.
    p0 = np.clip(p0, lo + 1e-9, hi - 1e-9)
    return least_squares(
        _residuals, p0, bounds=(lo, hi), args=(curves,), method="trf", max_nfev=2000
    )


def _bootstrap_kd(
    curves: list[_Curve],
    best: NDArray[np.float64],
    bounds: list[tuple[float, float]],
    n: int,
    seed: int,
) -> tuple[float, float]:
    preds = _predict(best, curves)
    resid = np.concatenate([c.y - pred for pred, c in zip(preds, curves, strict=True)])
    rng = np.random.default_rng(seed)
    kds: list[float] = []
    sizes = [c.t.size for c in curves]
    for _ in range(n):
        sampled = rng.choice(resid, size=resid.size, replace=True)
        boot = _rebuild(curves, preds, sampled, sizes)
        res = _solve(boot, best, bounds)
        kds.append(10.0 ** res.x[1] / 10.0 ** res.x[0])
    lo, hi = np.percentile(kds, [2.5, 97.5])
    return float(lo), float(hi)


def _rebuild(
    curves: list[_Curve],
    preds: list[NDArray[np.float64]],
    sampled: NDArray[np.float64],
    sizes: list[int],
) -> list[_Curve]:
    out: list[_Curve] = []
    start = 0
    for c, pred, size in zip(curves, preds, sizes, strict=True):
        y = pred + sampled[start : start + size]
        out.append(_Curve(c.t, y, c.conc_M, c.t_assoc_end))
        start += size
    return out


def fit_replicate(
    traces: list[Trace], model: str = "langmuir_1to1", bootstrap: int = 200, seed: int = 0
) -> KineticFit:
    """Globally fit one replicate's concentration series and return a KineticFit.

    `bootstrap` is the number of residual resamples for the K_D CI (0 disables).
    """
    if not traces:
        raise ValueError("fit_replicate requires at least one trace")
    curves = _to_curves(traces)
    p0, bounds = _initial(curves)
    res = _solve(curves, p0, bounds)
    kon, koff = 10.0 ** res.x[0], 10.0 ** res.x[1]
    kd = koff / kon
    ci = _bootstrap_kd(curves, res.x, bounds, bootstrap, seed) if bootstrap else (kd, kd)
    y_all = np.concatenate([c.y for c in curves])
    rel_mae = float(np.mean(np.abs(res.fun)) / (np.mean(np.abs(y_all)) + 1e-12))
    dof = max(y_all.size - len(res.x), 1)
    return KineticFit(
        name=traces[0].name,
        replicate=traces[0].replicate,
        model=model,
        kon=kon,
        koff=koff,
        kd_M=kd,
        kd_ci95=ci,
        rmax=res.x[2],
        chi2_red=float(np.sum(res.fun**2) / dof),
        rel_mae=rel_mae,
        n_points=int(y_all.size),
        converged=bool(res.success),
    )
