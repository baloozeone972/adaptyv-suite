"""Parse the on-disk package into typed objects.

Raw filenames are `<name>_<replicate>_<concentration>.csv`, and a name may itself
contain underscores. To parse unambiguously we take the known (name, replicate)
pairs from replicate_info.csv and match each raw file by its longest prefix.
"""

from __future__ import annotations

import csv
from pathlib import Path

from adaptyv_core.schemas import Method

from adaptyv_kinetics.schemas import ReplicateInfo, Trace


class PackageSchemaError(ValueError):
    """Raised when the package layout does not match the documented schema."""


def _opt_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def read_replicate_info(path: Path) -> list[ReplicateInfo]:
    """Parse aux/replicate_info.csv."""
    if not path.exists():
        raise PackageSchemaError(f"Missing replicate_info at {path}")
    out: list[ReplicateInfo] = []
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            out.append(
                ReplicateInfo(
                    name=row["name"],
                    replicate=int(row["replicate"]),
                    method=Method(row["method"]),
                    mae=_opt_float(row.get("MAE", "")),
                    rel_mae=_opt_float(row.get("rel_MAE", "")),
                    rmax_estimate=_opt_float(row.get("rmax_estimate", "")),
                )
            )
    return out


def _read_ty(path: Path) -> tuple[list[float], list[float]]:
    t: list[float] = []
    y: list[float] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != ["t", "y"]:
            raise PackageSchemaError(f"Expected columns t,y in {path}, got {reader.fieldnames}")
        for row in reader:
            t.append(float(row["t"]))
            y.append(float(row["y"]))
    return t, y


def _match_prefix(stem: str, pairs: list[tuple[str, int]]) -> tuple[str, int, float] | None:
    for name, rep in sorted(pairs, key=lambda p: len(p[0]), reverse=True):
        prefix = f"{name}_{rep}_"
        if stem.startswith(prefix):
            try:
                return name, rep, float(stem[len(prefix) :])
            except ValueError:
                return None
    return None


def read_traces(raw_dir: Path, infos: list[ReplicateInfo], is_control: bool = False) -> list[Trace]:
    """Parse every raw CSV under `raw_dir`, keyed to known (name, replicate) pairs."""
    pairs = [(i.name, i.replicate) for i in infos]
    traces: list[Trace] = []
    for csv_path in sorted(raw_dir.glob("*.csv")):
        matched = _match_prefix(csv_path.stem, pairs)
        if matched is None:
            continue
        name, rep, conc = matched
        t, y = _read_ty(csv_path)
        traces.append(
            Trace(name=name, replicate=rep, concentration_nM=conc, t=t, y=y, is_control=is_control)
        )
    return traces
