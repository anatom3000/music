import numpy as np

from synth import MAX_AMPLITUDE, Note, ADSR


class Noise:
    def __init__(self, volume: float):
        self.volume = volume

    def __call__(self, t: np.ndarray, sound: np.ndarray, note: Note):
        return sound + (np.random.random(sound.shape) * self.volume * MAX_AMPLITUDE)
