from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

from synth.constants import MAX_AMPLITUDE, SAMPLE_RATE
from synth.misc import Tone, Timbre


class Playable(ABC):
    start: float
    length: float

    @abstractmethod
    def generate(self, t: np.ndarray, max_amplitude: int) -> np.ndarray:
        pass


class Note(Playable):
    def __init__(self, tone: Tone, timbre: Timbre, start: float = 0.0, length: float = 1.0):
        self.tone = tone
        self.timbre = timbre

        self.start = start
        self.raw_length = length
        self.length = self.raw_length + self.timbre.enveloppe.release

    def generate(self, t: np.ndarray, max_amplitude: int) -> np.ndarray:
        # terrible, unoptimized code
        # if a numpy nerd can fix this I'd be grateful
        # (at least it works ?)
        sound = np.zeros(t.shape)
        for relative_frequency, relative_amplitude, oscillator in self.timbre.harmonics:
            sound += relative_amplitude * oscillator(t, relative_frequency * self.tone.frequency)

        sound *= self.timbre.enveloppe.get(t, self.raw_length)
        sound *= max_amplitude / np.max(sound)

        return sound.astype(np.int16)


class Sample(Playable):
    def __init__(self, file_path: Union[Path, str], start: float = 0.0, length: float = -1):
        self.file = file_path

        raw_sample_rate, self.data = wavfile.read(self.file)

        print("Resampling...")
        if raw_sample_rate != SAMPLE_RATE:
            print(f"Correcting rate from {raw_sample_rate} to {SAMPLE_RATE}")
            # https://stackoverflow.com/questions/64782091/how-to-resample-a-wav-sound-file-which-is-being-read-using-the-wavfile-read
            sample_number = round(self.data.shape[0] * float(SAMPLE_RATE) / raw_sample_rate)
            self.data = resample(self.data, sample_number)
        print("Resampled!")

        self.start = start

        if length > 0:
            self.data = self.data[:round(SAMPLE_RATE * length)]

        self.length = len(self.data) / SAMPLE_RATE

        self.data = (self.data / np.max(self.data) * MAX_AMPLITUDE).astype(np.int16)

    def generate(self, t: np.ndarray, max_amplitude: int) -> np.ndarray:
        time_frame = t.shape[0]
        return self.data[:time_frame]
