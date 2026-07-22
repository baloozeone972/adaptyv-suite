"""Langmuir 1:1 binding kinetics.

Association (0 <= t <= t_a), analyte concentration C (molar):

    R(t) = (C k_on R_max / (C k_on + k_off)) * (1 - exp(-(C k_on + k_off) t))

Dissociation (t > t_a):

    R(t) = R(t_a) * exp(-k_off (t - t_a))
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import median_filter

NM_TO_M = 1e-9


def response(
    t: NDArray[np.float64],
    kon: float,
    koff: float,
    rmax: float,
    conc_M: float,
    t_assoc_end: float,
    baseline: float = 0.0,
) -> NDArray[np.float64]:
    """Model response over `t` for one curve at concentration `conc_M`.

    >>> import numpy as np
    >>> r = response(np.array([0.0, 100.0]), 1e5, 1e-3, 1.0, 1e-8, 120.0)
    >>> r[0] == 0.0
    True
    """
    kobs = conc_M * kon + koff
    r_at_end = (conc_M * kon * rmax / kobs) * (1.0 - np.exp(-kobs * t_assoc_end))
    assoc = (conc_M * kon * rmax / kobs) * (1.0 - np.exp(-kobs * np.minimum(t, t_assoc_end)))
    dissoc = r_at_end * np.exp(-koff * np.maximum(t - t_assoc_end, 0.0))
    return baseline + np.where(t <= t_assoc_end, assoc, dissoc)


def infer_assoc_end(t: NDArray[np.float64], y: NDArray[np.float64]) -> float:
    """Infer the association/dissociation split as the peak of a median-filtered curve.

    A median filter (not a boxcar) is deliberate: it removes single-point spikes
    that would fool a raw argmax, yet it does not shift a broad peak the way a
    moving average does — so the split stays unbiased on clean data.

    >>> import numpy as np
    >>> infer_assoc_end(np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 0.5]))
    1.0
    """
    if y.size < 5:
        return float(t[int(np.argmax(y))])
    filtered = median_filter(y, size=5, mode="nearest")
    return float(t[int(np.argmax(filtered))])
