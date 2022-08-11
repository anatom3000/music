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
    def __init__(self, frequency: float, amplitude: float, center: float = 0.0, oscillator: oscillators.Oscillator = oscillators.sine):
        self.oscillator = oscillator
        self.center = center
        self.amplitude = amplitude
        self.frequency = frequency

    def get_value(self, t: np.ndarray) -> np.ndarray:
        return self.amplitude*self.oscillator(t, self.frequency) + self.center


class LinearTransition(EffectModulator):
    def __init__(self, start_time: float, start_value: float, end_time: float, end_value: float):
        self.start_time = start_time
        self.start_value = start_value
        self.end_time = end_time
        self.end_value = end_value

    def get_value(self, t: np.ndarray) -> np.ndarray:
        return np.interp(t, (self.start_time, self.end_time), (self.start_value, self.end_value))
