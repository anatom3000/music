from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from .. import oscillators


class EffectModulator(ABC):
    @abstractmethod
    def get_value(self, t: np.ndarray) -> np.ndarray:
        pass

    @classmethod
    def handle(cls, value: EffectModulator | Any, t: np.ndarray) -> np.ndarray | Any:
        if isinstance(value, cls):
            return value.get_value(t)
        else:
            return value


class LFO(EffectModulator):
    def get_value(self, t: np.ndarray) -> np.ndarray:
        return self.amplitude*self.oscillator(t, self.frequency) + self.center

    def __init__(self, frequency: float, amplitude: float, center: float = 0.0, oscillator: oscillators.Oscillator = oscillators.sine):
        self.oscillator = oscillator
        self.center = center
        self.amplitude = amplitude
        self.frequency = frequency
