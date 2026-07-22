"""Shared fixtures. Calibration fits many curves, so compute it once per session."""

from __future__ import annotations

import pytest
from sensorgram_triage.delegation import calibrate
from sensorgram_triage.labels import Dataset, synthetic_dataset
from sensorgram_triage.model import LogisticModel
from sensorgram_triage.schemas import DelegationCurve


@pytest.fixture(scope="session")
def dataset() -> Dataset:
    return synthetic_dataset(n_good=8, n_bad=6, seed=0)


@pytest.fixture(scope="session")
def calibrated() -> tuple[LogisticModel, DelegationCurve]:
    return calibrate(n_good=8, n_bad=6, seed=0)
