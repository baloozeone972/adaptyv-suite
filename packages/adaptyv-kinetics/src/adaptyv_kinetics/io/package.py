"""The DataPackage façade — the public entry point of the library."""

from __future__ import annotations

import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

import polars as pl

from adaptyv_kinetics.io.parsers import PackageSchemaError, read_replicate_info, read_traces
from adaptyv_kinetics.models.fitting import fit_replicate
from adaptyv_kinetics.qc.rules import evaluate
from adaptyv_kinetics.report.html import build_report
from adaptyv_kinetics.schemas import KineticFit, ReplicateInfo, Trace, TraceVerdict


class DataPackage:
    """A parsed binding data package. Build it with `from_zip` or `from_dir`."""

    def __init__(self, infos: list[ReplicateInfo], traces: list[Trace]) -> None:
        self._infos = infos
        self._traces = traces

    @classmethod
    def from_dir(cls, path: str | Path) -> DataPackage:
        """Parse a package directory tree."""
        root = Path(path)
        raw = root / "raw_data"
        if not raw.is_dir():
            raise PackageSchemaError(f"No raw_data/ directory under {root}")
        infos = read_replicate_info(root / "aux" / "replicate_info.csv")
        return cls(infos, read_traces(raw, infos))

    @classmethod
    def from_zip(cls, path: str | Path) -> DataPackage:
        """Extract and parse a package .zip.

        Extraction is guarded against path traversal ("zip slip"): any member
        whose resolved path would escape the temporary directory is rejected.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root_dir = Path(tmp).resolve()
            with zipfile.ZipFile(path) as zf:
                _safe_extract(zf, root_dir)
            return cls.from_dir(_find_root(root_dir))

    def traces(self) -> list[Trace]:
        """All raw traces in the package."""
        return list(self._traces)

    def replicate_infos(self) -> list[ReplicateInfo]:
        """The parsed replicate metadata."""
        return list(self._infos)

    def _grouped(self) -> dict[tuple[str, int], list[Trace]]:
        groups: dict[tuple[str, int], list[Trace]] = defaultdict(list)
        for tr in self._traces:
            if not tr.is_control:
                groups[(tr.name, tr.replicate)].append(tr)
        return groups

    def summary(self) -> pl.DataFrame:
        """One row per replicate: name, replicate, method, MAE, rel_MAE, Rmax estimate."""
        return pl.DataFrame(
            [
                {
                    "name": i.name,
                    "replicate": i.replicate,
                    "method": i.method.value,
                    "mae": i.mae,
                    "rel_mae": i.rel_mae,
                    "rmax_estimate": i.rmax_estimate,
                }
                for i in self._infos
            ]
        )

    def refit(self, model: str = "langmuir_1to1", bootstrap: int = 200) -> list[KineticFit]:
        """Independently re-fit every replicate."""
        return [
            fit_replicate(traces, model=model, bootstrap=bootstrap)
            for traces in self._grouped().values()
        ]

    def qc(self, bootstrap: int = 200) -> list[TraceVerdict]:
        """Run QC on every replicate, returning a verdict with flags and the fit."""
        return [evaluate(traces, bootstrap=bootstrap) for traces in self._grouped().values()]

    def compare_fits(self, bootstrap: int = 0) -> pl.DataFrame:
        """Compare the independent re-fit against the values shipped in the package.

        This is the independent-verifier view: where the re-fit agrees with the
        package's own numbers it is evidence of quality; where it diverges it is
        information to investigate — never presented as "their error".
        """
        reported = {(i.name, i.replicate): i for i in self._infos}
        rows: list[dict[str, object]] = []
        for fit in self.refit(bootstrap=bootstrap):
            info = reported.get((fit.name, fit.replicate))
            rmax_ref = info.rmax_estimate if info else None
            pct = (
                abs(fit.rmax - rmax_ref) / rmax_ref * 100.0 if rmax_ref not in (None, 0.0) else None
            )
            rows.append(
                {
                    "name": fit.name,
                    "replicate": fit.replicate,
                    "kd_nM_refit": fit.kd_M * 1e9,
                    "rmax_refit": fit.rmax,
                    "rmax_reported": rmax_ref,
                    "rmax_pct_diff": pct,
                    "rel_mae_refit": fit.rel_mae,
                    "rel_mae_reported": info.rel_mae if info else None,
                }
            )
        return pl.DataFrame(rows)

    def report(self, out: str | Path, bootstrap: int = 200) -> Path:
        """Render a self-contained HTML QC report."""
        return build_report(self, Path(out), bootstrap=bootstrap)


def _safe_extract(zf: zipfile.ZipFile, dest: Path) -> None:
    """Extract every member, refusing any that would escape `dest` (zip slip)."""
    for member in zf.namelist():
        target = (dest / member).resolve()
        if not target.is_relative_to(dest):
            raise PackageSchemaError(f"Refusing unsafe path in archive: {member!r}")
    zf.extractall(dest)


def _find_root(extracted: Path) -> Path:
    if (extracted / "raw_data").is_dir():
        return extracted
    for child in extracted.iterdir():
        if child.is_dir() and (child / "raw_data").is_dir():
            return child
    raise PackageSchemaError(f"Could not locate raw_data/ under {extracted}")
