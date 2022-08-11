from __future__ import annotations

from abc import ABC

import numpy as np
import pyrubberband

from ..constants import MAX_AMPLITUDE, SAMPLE_RATE
from . import modulators


class Effect(ABC):
    def preprocess(self, playable: Playable):
        pass

    def postprocess(self, t: np.ndarray, sound: np.ndarray, p: Playable) -> np.ndarray:
        return sound


class Noise(Effect):
    def __init__(self, volume: float | modulators.EffectModulator):
        self.volume = volume

    def postprocess(self, t: np.ndarray, sound: np.ndarray, _p: Playable) -> np.ndarray:
        return sound + (np.random.random(sound.shape) * modulators.EffectModulator.handle(self.volume, t) * MAX_AMPLITUDE)


class Normalize(Effect):
    def postprocess(self, _t: np.ndarray, sound: np.ndarray, p: Playable) -> np.ndarray:
        return sound * p.volume * MAX_AMPLITUDE / np.max(sound)


class Transpose(Effect):
    def __init__(self, interval: int | modulators.EffectModulator):
        self.interval = interval

    def postprocess(self, t: np.ndarray, sound: np.ndarray, _p: Playable) -> np.ndarray:
        if self.interval != 0:
            return (MAX_AMPLITUDE * pyrubberband.pyrb.pitch_shift(sound.astype(np.float64) / MAX_AMPLITUDE,
                                                                  sr=SAMPLE_RATE, n_steps=modulators.EffectModulator.handle(self.interval, t))).astype(
                np.int16)
        else:
            return sound


class Scratch(Effect):
    def __init__(self, percentage: float | modulators.EffectModulator = 0.02):
        self.percentage = percentage

    def postprocess(self, t: np.ndarray, sound: np.ndarray, _p: Playable) -> np.ndarray:
        mask = np.random.random(sound.shape) < modulators.EffectModulator.handle(self.percentage, t)
        noise = np.random.random(sound.shape) * MAX_AMPLITUDE

        return np.where(mask, noise, sound)


class LowPassFilter(Effect):
    def __init__(self, interval: int):
        self.interval = interval

    def postprocess(self, _t: np.ndarray, sound: np.ndarray, _p: Playable) -> np.ndarray:
        pass
