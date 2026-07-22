"""boltz-tune — a reproducible learning-curve harness for affinity fine-tuning."""

from boltz_tune.curve import evaluate, fit_curve
from boltz_tune.data import BASE_SCORE, synthetic_sweep
from boltz_tune.schemas import LearningCurve, TrainingObservation, TuneResult

__all__ = [
    "BASE_SCORE",
    "LearningCurve",
    "TrainingObservation",
    "TuneResult",
    "evaluate",
    "fit_curve",
    "synthetic_sweep",
]
__version__ = "0.0.1"
