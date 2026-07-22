"""A small, dependency-free logistic regression.

Deterministic (zero init, full-batch gradient descent), so training is reproducible
and 100% testable without a heavy ML dependency. The point of spec H is calibration
and the delegation curve, not model sophistication — this is enough to rank curves.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def _sigmoid(z: Array) -> Array:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))


@dataclass
class LogisticModel:
    """Standardized logistic regression: P(needs review) from a feature vector."""

    weights: Array
    bias: float
    mean: Array
    std: Array

    @classmethod
    def fit(
        cls, x: Array, y: Array, epochs: int = 2000, lr: float = 0.1, l2: float = 1e-3
    ) -> LogisticModel:
        """Fit by full-batch gradient descent on standardized features."""
        mean = x.mean(axis=0)
        std = x.std(axis=0)
        std[std == 0] = 1.0
        xs = (x - mean) / std
        n, d = xs.shape
        w = np.zeros(d)
        b = 0.0
        for _ in range(epochs):
            p = _sigmoid(xs @ w + b)
            error = p - y
            w -= lr * (xs.T @ error / n + l2 * w)
            b -= lr * float(error.mean())
        return cls(weights=w, bias=b, mean=mean, std=std)

    def predict_proba(self, x: Array) -> Array:
        """Return P(needs review) for each row of `x`."""
        xs = (x - self.mean) / self.std
        return _sigmoid(xs @ self.weights + self.bias)
