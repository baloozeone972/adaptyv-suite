"""Data ingestion: a synthetic generator (declared) and a CSV loader.

The synthetic set mimics Proteinbase structure — several campaigns, design methods,
in-silico scores of varying predictive power, and wet-lab outcomes. Point the CSV
loader at a real Proteinbase export to run the same analysis on real data.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from insilico_bench.schemas import DesignRecord

_METHODS = ("RFdiffusion", "BindCraft", "Mosaic", "PXDesign")
_META_COLUMNS = {"name", "campaign", "method", "is_binder", "pkd"}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def synthetic_dataset(
    seed: int = 0,
    campaigns: tuple[str, ...] = ("egfr_r1", "nipah", "trem2"),
    n_per_campaign: int = 60,
) -> list[DesignRecord]:
    """Generate a labelled dataset where ipSAE > ipTM > pLDDT in predictive power."""
    rng = np.random.default_rng(seed)
    records: list[DesignRecord] = []
    for campaign in campaigns:
        for i in range(n_per_campaign):
            quality = float(rng.normal(0.0, 1.0))
            is_binder = rng.random() < _sigmoid(1.4 * quality - 0.5)
            pkd = 7.0 + 1.5 * quality + float(rng.normal(0, 0.3)) if is_binder else None
            scores = {
                "ipsae": 0.55 + 0.16 * quality + float(rng.normal(0, 0.05)),
                "iptm": 0.55 + 0.09 * quality + float(rng.normal(0, 0.12)),
                "plddt": 72.0 + 2.0 * quality + float(rng.normal(0, 6.0)),
            }
            records.append(
                DesignRecord(
                    name=f"{campaign}_{i:03d}",
                    campaign=campaign,
                    method=_METHODS[i % len(_METHODS)],
                    scores=scores,
                    is_binder=bool(is_binder),
                    pkd=pkd,
                )
            )
    return records


def load_csv(path: str | Path) -> list[DesignRecord]:
    """Load records from a CSV: name, campaign, method, is_binder, pkd + score columns."""
    records: list[DesignRecord] = []
    with Path(path).open(newline="") as fh:
        reader = csv.DictReader(fh)
        score_cols = [c for c in (reader.fieldnames or []) if c not in _META_COLUMNS]
        for row in reader:
            pkd = row.get("pkd", "").strip()
            records.append(
                DesignRecord(
                    name=row["name"],
                    campaign=row["campaign"],
                    method=row.get("method", "unknown"),
                    scores={c: float(row[c]) for c in score_cols if row.get(c, "").strip()},
                    is_binder=row["is_binder"].strip().lower() in {"1", "true", "yes"},
                    pkd=float(pkd) if pkd else None,
                )
            )
    return records


def write_csv(records: list[DesignRecord], path: str | Path) -> Path:
    """Write records to CSV (round-trips with load_csv)."""
    path = Path(path)
    score_cols = sorted({s for r in records for s in r.scores})
    fields = ["name", "campaign", "method", "is_binder", "pkd", *score_cols]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in records:
            row: dict[str, object] = {
                "name": r.name,
                "campaign": r.campaign,
                "method": r.method,
                "is_binder": int(r.is_binder),
                "pkd": "" if r.pkd is None else r.pkd,
            }
            row.update({c: r.scores.get(c, "") for c in score_cols})
            writer.writerow(row)
    return path
