import numpy as np

from synth import MAX_AMPLITUDE


class Noise:
    def __init__(self, volume: float):
        self.volume = volume

    def __call__(self, sound: np.ndarray):
        return sound + (np.random.random(sound.shape) * self.volume * MAX_AMPLITUDE)
