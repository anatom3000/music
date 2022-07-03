from typing import Union, Optional

import numpy as np

EPSILON = 1e-6


class ADSR:
    """
    Modified version of the ADSR class from torchsynth
        => https://github.com/torchsynth/torchsynth/blob/4f3be6532a80b3298958eb5eca2f653a80ec7562/torchsynth/module.py#L317=
    Can be used for the pitch or the amplitude enveloppe
    """

    def __init__(self, *, attack: float, decay: float, sustain: float, release: float):
        self.attack = attack + EPSILON
        self.decay = decay + EPSILON
        self.sustain = sustain + EPSILON
        self.release = release + EPSILON

    def get(self, t: np.ndarray, duration: Union[np.ndarray, float]) -> np.ndarray:
        # Calculations to accommodate attack/decay phase cut by note duration.
        new_attack = np.minimum(self.attack, duration)
        new_decay = np.clip(duration - self.attack, 0.0, self.decay)

        attack_signal = ADSR.ramp(t, new_attack)

        a = 1.0 - self.sustain
        b = self.ramp(t, new_decay, start=new_attack, inverse=True)
        decay_signal = a * b + self.sustain

        release_signal = self.ramp(t, self.release, start=duration, inverse=True)

        return attack_signal * decay_signal * release_signal

    def __mul__(self, other: float) -> 'ADSR':
        return self.__class__(
            attack=self.attack * other,
            decay=self.decay * other,
            sustain=self.sustain * other,
            release=self.release * other
        )

    @staticmethod
    def ramp(t: np.ndarray, duration: Optional[Union[np.ndarray, float]] = None, start: Union[np.ndarray, float] = 0.0,
             inverse: bool = False) -> np.ndarray:
        duration = t.shape[0] if duration is None else duration

        y = t - start
        y = np.clip(y / duration, 0.0, 1.0)

        if inverse:
            y = np.where(duration > 0.0, 1.0 - y, y)

        return y
