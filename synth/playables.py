from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np
import pygame
from scipy.io import wavfile
from scipy.signal import resample

from synth.constants import MAX_AMPLITUDE, SAMPLE_RATE

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


class Playable(ABC):
    start: float
    length: float
    volume: float

    @property
    def end(self):
        return self.start + self.length

    @abstractmethod
    def generate(self) -> np.ndarray:
        pass

    @staticmethod
    def play(samples: np.ndarray, *, wait: bool = True) -> None:
        sound = pygame.sndarray.make_sound(samples)
        sound.play(-1)
        if wait:
            pygame.time.wait(int(samples.shape[0] / SAMPLE_RATE * 1000))
            pygame.mixer.stop()

    def generate_and_play(self, *, wait: bool = True, debug: bool = False) -> None:
        if debug:
            print("Starting generating sound...")
        samples = self.generate()
        if debug:
            print("Finished generating, started playing...")
        self.play(samples, wait=wait)
        if debug:
            print("Finished playing!")


class Sample(Playable):
    def __init__(self, file_path: Union[Path, str], start: float = 0.0, length: float = -1, volume: float = 1.0):
        self.file = file_path

        raw_sample_rate, self.data = wavfile.read(self.file)

        if raw_sample_rate != SAMPLE_RATE:
            # https://stackoverflow.com/questions/64782091/how-to-resample-a-wav-sound-file-which-is-being-read-using-the-wavfile-read
            sample_number = round(self.data.shape[0] * float(SAMPLE_RATE) / raw_sample_rate)
            self.data = resample(self.data, sample_number)

        self.start = start
        self.volume = volume

        if length > 0:
            self.data = self.data[:round(SAMPLE_RATE * length)]

        self.length = len(self.data) / SAMPLE_RATE

        self.data = (self.data / np.max(self.data) * MAX_AMPLITUDE).astype(np.int16)

    def generate(self) -> np.ndarray:
        local_data = self.data.copy()
        local_data.resize(round(self.length*SAMPLE_RATE))
        return local_data * self.volume
