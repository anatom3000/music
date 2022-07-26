import numpy as np
import pyrubberband

from synth import MAX_AMPLITUDE, SAMPLE_RATE, Playable


class Noise:
    def __init__(self, volume: float):
        self.volume = volume

    def __call__(self, t: np.ndarray, sound: np.ndarray, p: Playable):
        return sound + (np.random.random(sound.shape) * self.volume * MAX_AMPLITUDE)


def normalize(t: np.ndarray, sound: np.ndarray, p: Playable):
    return sound * p.volume * MAX_AMPLITUDE / np.max(sound)


class Transpose:
    def __init__(self, interval: int):
        self.interval = interval

    def __call__(self, t: np.ndarray, sound: np.ndarray, p: Playable):
        if self.interval != 0:
            return (MAX_AMPLITUDE*pyrubberband.pyrb.pitch_shift(sound.astype(np.float64)/MAX_AMPLITUDE, sr=SAMPLE_RATE, n_steps=self.interval)).astype(np.int16)
        else:
            return sound


class Scratch:
    def __init__(self, percentage: float = 0.02):
        self.percentage = percentage

    def __call__(self, t: np.ndarray, sound: np.ndarray, p: Playable):
        mask = np.random.random(sound.shape) < self.percentage
        noise = np.random.random(sound.shape) * MAX_AMPLITUDE

        return np.where(mask, noise, sound)


class LowPassFilter:
    def __init__(self, interval: int):
        self.interval = interval

    def __call__(self, t: np.ndarray, sound: np.ndarray, p: Playable):
        if self.interval != 0:
            return (MAX_AMPLITUDE*pyrubberband.pyrb.pitch_shift(sound.astype(np.float64)/MAX_AMPLITUDE, sr=SAMPLE_RATE, n_steps=self.interval)).astype(np.int16)
        else:
            return sound