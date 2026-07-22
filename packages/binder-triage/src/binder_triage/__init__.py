"""binder-triage — diversity-aware selection of designs under a plate budget."""

from binder_triage.evaluate import compare, evaluate
from binder_triage.pool import synthetic_pool
from binder_triage.schemas import Candidate, Selection
from binder_triage.select import diverse_greedy, top_n

__all__ = [
    "Candidate",
    "Selection",
    "compare",
    "diverse_greedy",
    "evaluate",
    "synthetic_pool",
    "top_n",
]
__version__ = "0.0.1"
