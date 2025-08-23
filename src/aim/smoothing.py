"""Smoothing utilities for Aim Mode."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EMA:
    """Simple exponential moving average filter."""

    alpha: float
    value: float = 0.0

    def update(self, sample: float) -> float:
        self.value = self.alpha * sample + (1 - self.alpha) * self.value
        return self.value
