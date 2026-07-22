"""Weakly-labelled synthetic dataset.

Clean binders are labelled "good" (auto-approvable); non-binders and
artifact-injected curves are labelled "needs review". Because we generate them, the
labels are known — which is what makes the delegation curve measurable. On real
data these labels come from Adaptyv's review decisions; this is the harness.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator

from sensorgram_triage.features import extract

_BAD_KINDS = ("non_binder", "incomplete_dissociation", "spike")


@dataclass(frozen=True, slots=True)
class Dataset:
    """Feature matrix, labels (1 = needs review), and group ids (protein names)."""

    x: np.ndarray
    y: np.ndarray
    groups: list[str]


def _build_package(gen: PackageGenerator, n_good: int, n_bad: int) -> None:
    # Good binders span a range of measurement noise: the noisiest ones look
    # borderline, so the model cannot separate perfectly — a realistic trade-off.
    for i in range(n_good):
        noise = 0.005 + 0.010 * (i % 6)
        gen.add_protein(
            f"good_{i:02d}", kd_nM=float(3 + 4 * i), rmax=0.8, replicates=2, noise=noise
        )
    for i in range(n_bad):
        kind = _BAD_KINDS[i % len(_BAD_KINDS)]
        name = f"bad_{i:02d}"
        if kind == "non_binder":
            gen.add_protein(name, non_binder=True, replicates=2)
        else:
            gen.add_protein(name, kd_nM=40.0, artifacts=[kind], replicates=2)


def synthetic_dataset(n_good: int = 12, n_bad: int = 9, seed: int = 0) -> Dataset:
    """Generate a labelled dataset by fabricating good and problematic packages."""
    gen = PackageGenerator(seed=seed)
    _build_package(gen, n_good, n_bad)
    with tempfile.TemporaryDirectory() as tmp:
        root = gen.write_dir(Path(tmp) / "pkg")
        rows = extract(DataPackage.from_dir(root).traces())
    x = np.vstack([r.vector for r in rows])
    y = np.array([1.0 if r.name.startswith("bad") else 0.0 for r in rows], dtype=np.float64)
    groups = [r.name for r in rows]
    return Dataset(x=x, y=y, groups=groups)
