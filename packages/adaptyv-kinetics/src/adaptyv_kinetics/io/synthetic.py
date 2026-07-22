"""Synthetic binding-data-package generator.

Doubles as the validation harness: because the true parameters are known, the
recovery error of the fitter can be measured. The on-disk layout follows the
schema verified against Adaptyv's live docs (raw_data/, fit_data/,
aux/replicate_info.csv).
"""

from __future__ import annotations

import csv
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from adaptyv_kinetics.models.langmuir import NM_TO_M, response

# A proper kinetics run needs a dissociation window long enough to identify
# k_off; too short and K_D = k_off/k_on is only weakly determined. These defaults
# give ~45% dissociation at k_off ~1e-3, so recovery stays accurate.
_T_ASSOC = 180.0
_T_DISSOC = 480.0
_DT = 4.0
_DEFAULT_CONC_NM = (3.125, 6.25, 12.5, 25.0, 50.0)


@dataclass
class ProteinSpec:
    """Ground-truth specification for one synthetic protein."""

    name: str
    kd_nM: float = 10.0
    kon: float = 1e5
    rmax: float = 0.8
    replicates: int = 2
    artifacts: list[str] = field(default_factory=list)
    non_binder: bool = False
    noise: float = 0.01


def _time_grid() -> np.ndarray:
    return np.arange(0.0, _T_ASSOC + _T_DISSOC + _DT, _DT)


def _clean_curve(spec: ProteinSpec, conc_nM: float) -> np.ndarray:
    t = _time_grid()
    if spec.non_binder:
        return np.zeros_like(t)
    koff = spec.kd_nM * NM_TO_M * spec.kon
    return response(t, spec.kon, koff, spec.rmax, conc_nM * NM_TO_M, _T_ASSOC)


def _apply_artifacts(
    t: np.ndarray, y: np.ndarray, spec: ProteinSpec, rng: np.random.Generator
) -> np.ndarray:
    out = y.copy()
    if "baseline_drift" in spec.artifacts:
        out = out + (t / t[-1]) * 0.4 * spec.rmax
    if "spike" in spec.artifacts:
        out[rng.integers(0, out.size)] += 0.5 * spec.rmax
    if "incomplete_dissociation" in spec.artifacts:
        mask = t > _T_ASSOC
        out[mask] = out[t <= _T_ASSOC][-1]  # response frozen; koff unidentifiable
    return out


@dataclass
class PackageGenerator:
    """Build a schema-conformant synthetic package. Seeded for reproducibility."""

    seed: int = 42
    _specs: list[ProteinSpec] = field(default_factory=list)

    def add_protein(self, name: str, **kwargs: object) -> PackageGenerator:
        """Register a protein by its ground-truth parameters (see ProteinSpec)."""
        self._specs.append(ProteinSpec(name=name, **kwargs))  # type: ignore[arg-type]
        return self

    def _rows(
        self, spec: ProteinSpec, rep: int, rng: np.random.Generator
    ) -> list[tuple[float, np.ndarray, np.ndarray]]:
        t = _time_grid()
        rows = []
        for conc in _DEFAULT_CONC_NM:
            clean = _clean_curve(spec, conc)
            noisy = _apply_artifacts(t, clean, spec, rng) + rng.normal(0.0, spec.noise, t.size)
            rows.append((conc, t, np.round(noisy, 3)))
        return rows

    def write_dir(self, root: str | Path) -> Path:
        """Write the package as a directory tree and return its path."""
        root = Path(root)
        (root / "raw_data").mkdir(parents=True, exist_ok=True)
        (root / "fit_data").mkdir(parents=True, exist_ok=True)
        (root / "aux").mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(self.seed)
        info: list[dict[str, object]] = []
        for spec in self._specs:
            for rep in range(1, spec.replicates + 1):
                for conc, t, y in self._rows(spec, rep, rng):
                    self._write_csv(root / "raw_data" / f"{spec.name}_{rep}_{conc}.csv", t, y)
                    self._write_csv(
                        root / "fit_data" / f"{spec.name}_{rep}_{conc}.csv",
                        t,
                        _clean_curve(spec, conc),
                    )
                info.append(self._info_row(spec, rep))
        self._write_info(root / "aux" / "replicate_info.csv", info)
        return root

    def write_zip(self, path: str | Path) -> Path:
        """Write the package as a .zip and return its path (no temp dir left behind)."""
        path = Path(path)
        with tempfile.TemporaryDirectory() as tmp:
            root = self.write_dir(Path(tmp) / "package")
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in sorted(root.rglob("*")):
                    if f.is_file():
                        zf.write(f, f.relative_to(root))
        return path

    @staticmethod
    def _write_csv(path: Path, t: np.ndarray, y: np.ndarray) -> None:
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["t", "y"])
            w.writerows(zip(t.tolist(), y.tolist(), strict=True))

    @staticmethod
    def _info_row(spec: ProteinSpec, rep: int) -> dict[str, object]:
        return {
            "name": spec.name,
            "replicate": rep,
            "method": "BLI",
            "MAE": round(spec.noise, 2),
            "rel_MAE": round(spec.noise / max(spec.rmax, 1e-6), 2),
            "rmax_estimate": round(0.0 if spec.non_binder else spec.rmax, 3),
        }

    @staticmethod
    def _write_info(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(
                fh, fieldnames=["name", "replicate", "method", "MAE", "rel_MAE", "rmax_estimate"]
            )
            w.writeheader()
            w.writerows(rows)
