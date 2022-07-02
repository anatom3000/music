import wave
from pathlib import Path
from typing import Union

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

from . import Playable, SAMPLE_RATE, MAX_AMPLITUDE


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
