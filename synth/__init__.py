from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np
import pygame

SAMPLE_RATE = 44100  # Hz
MAX_AMPLITUDE = 4096

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


def normalize(arr: np.ndarray, *, volume: float = 1.0) -> np.ndarray:
    arr = arr / np.max(arr)
    arr *= MAX_AMPLITUDE * volume
    return arr


def play(samples: np.ndarray, *, wait: bool = True) -> None:
    sound = pygame.sndarray.make_sound(samples)
    sound.play(-1)
    if wait:
        pygame.time.wait(int(samples.shape[0] / SAMPLE_RATE * 1000))
        pygame.mixer.stop()


class Playable(ABC):
    start: float
    length: float

    @abstractmethod
    def generate(self, t: np.ndarray) -> np.ndarray:
        pass


class Song:
    def __init__(self, notes: Sequence[Playable]):
        self.notes = sorted(notes, key=lambda x: x.start)
        self.length = max(map(lambda x: x.start + x.length, self.notes))

        self.min_buffer_time = 1.0
        self.extra_time = 1.0

        self.time_generated = 0.0

    def generate(self) -> np.ndarray:
        t = np.linspace(0, self.length, round((self.length * SAMPLE_RATE)))
        samples = np.zeros(t.shape, dtype=np.int16)
        for i, note in enumerate(self.notes):
            sampled_start = round(SAMPLE_RATE * note.start)

            sampled_audio = note.generate(t[sampled_start:] - note.start)
            sampled_audio *= MAX_AMPLITUDE / np.max(sampled_audio)

            samples[sampled_start:] += sampled_audio.astype(np.int16)
            samples.clip(-MAX_AMPLITUDE, MAX_AMPLITUDE)

            self.time_generated = note.start

        return samples

    def generate_and_play(self, *, wait: bool = True, debug: bool = False) -> None:
        if debug:
            print("Starting generating sound...")
        samples = self.generate()
        if debug:
            print("Finished generating, started playing...")
        play(samples, wait=wait)
        if debug:
            print("Finished playing!")
