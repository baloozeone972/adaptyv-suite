"""Export re-fit results to standard tabular formats."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from adaptyv_kinetics.schemas import KineticFit


def fits_to_frame(fits: list[KineticFit]) -> pl.DataFrame:
    """Flatten a list of KineticFit into a Polars DataFrame."""
    return pl.DataFrame(
        [
            {
                "name": f.name,
                "replicate": f.replicate,
                "model": f.model,
                "kon": f.kon,
                "koff": f.koff,
                "kd_M": f.kd_M,
                "kd_nM": f.kd_M * 1e9,
                "kd_ci95_low_nM": f.kd_ci95[0] * 1e9,
                "kd_ci95_high_nM": f.kd_ci95[1] * 1e9,
                "rmax": f.rmax,
                "chi2_red": f.chi2_red,
                "rel_mae": f.rel_mae,
                "n_points": f.n_points,
                "converged": f.converged,
            }
            for f in fits
        ]
    )


def export_fits(fits: list[KineticFit], path: str | Path, fmt: str = "csv") -> Path:
    """Write fits to `path` in the given format (csv | parquet | json)."""
    path = Path(path)
    frame = fits_to_frame(fits)
    if fmt == "csv":
        frame.write_csv(path)
    elif fmt == "parquet":
        frame.write_parquet(path)
    elif fmt == "json":
        frame.write_json(path)
    else:
        raise ValueError(f"Unknown format {fmt!r}; expected csv, parquet or json")
    return path
