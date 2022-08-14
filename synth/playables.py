from __future__ import annotations

import copy
import pathlib
import struct
import wave
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Union

import numpy as np
import pygame
import pyrubberband as pyrubberband
from librosa import load as rosaload

from .constants import MAX_AMPLITUDE, SAMPLE_RATE
from .effects import Effect
from .oscillators import Oscillator, sine

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


class Playable(ABC):
    start: float
    length: float
    volume: float
    effects: Sequence[Effect]

    @property
    def end(self):
        return self.start + self.length

    @abstractmethod
    def generate_raw(self, t) -> np.ndarray:
        pass

    def generate(self):
        for e in self.effects:
            e.preprocess(self)

        t = np.linspace(0, self.length, round((self.length * SAMPLE_RATE)))
        sound = self.generate_raw(t)
        for e in self.effects:
            sound = e.postprocess(t, sound, self)

        return (sound * self.volume * MAX_AMPLITUDE / np.max(sound)).astype(np.int16)

    @staticmethod
    def play(samples: np.ndarray, *, wait: bool = True) -> pygame.mixer.Channel:
        sound = pygame.sndarray.make_sound(samples)
        channel = sound.play(-1)
        if wait:
            pygame.time.wait(int(samples.shape[0] / SAMPLE_RATE * 1000))
            pygame.mixer.stop()
        return channel

    @staticmethod
    def save(samples: np.ndarray, path: Union[str, pathlib.Path]):
        with wave.open(path, mode='w') as f:
            f.setnchannels(1)  # mono
            f.setsampwidth(2)
            f.setframerate(SAMPLE_RATE)
            for i in samples:
                f.writeframesraw(struct.pack('<h', i))

    def generate_and_play(self, *, wait: bool = True, debug: bool = False) -> pygame.mixer.Channel:
        if debug:
            print("Starting generating sound...")
        samples = self.generate()
        if debug:
            print("Finished generating, started playing...")
        channel = self.play(samples, wait=wait)
        if debug:
            print("Finished playing!")
        return channel

    def generate_and_save(self, path: Union[str, pathlib.Path]):
        samples = self.generate()
        self.save(samples, path)


class Noise(Playable):
    def __init__(self, length: float, start: float = 0.0, volume: float = 1.0):
        self.start = start
        self.length = length
        self.volume = volume

    def generate_raw(self, t: np.ndarray) -> np.ndarray:
        return np.random.random(t.shape) * self.volume * MAX_AMPLITUDE


class Sample(Playable):
    def __init__(self, file_path: Union[Path, str], offset: float = 0.0, start: float = 0.0, length: float = None,
                 volume: float = 1.0, effects: Sequence[Effect] = None):
        self.data, _ = rosaload(file_path, sr=SAMPLE_RATE, mono=True, offset=offset, duration=length)

        self.start = start
        self.length = self.data.shape[0] / SAMPLE_RATE if length is None else length
        self.volume = volume
        self.effects = [] if effects is None else effects

        self.data = self.data / np.max(self.data) * MAX_AMPLITUDE * self.volume

    def generate_raw(self, t: np.ndarray) -> np.ndarray:
        return self.data

    def transpose(self, interval: int):
        if interval != 0:
            self.data = (MAX_AMPLITUDE * pyrubberband.pyrb.pitch_shift(self.data.astype(np.float64) / MAX_AMPLITUDE,
                                                                       sr=SAMPLE_RATE, n_steps=interval)).astype(
                np.int16)

    def transposed(self, interval: int):
        new = copy.deepcopy(self)
        new.transpose(interval)
        return new

    def __add__(self, other):
        return self.transposed(other)

    def __sub__(self, other):
        return self.transposed(-other)


class PlayableOscillator(Playable):
    def __init__(self, frequency: float = 440, oscillator: Oscillator = sine, start: float = 0.0, length: float = 1.0,
                 volume: float = 1.0, effects: Sequence[Effect] = None):
        self.frequency = frequency
        self.oscillator = oscillator

        self.start = start
        self.length = length
        self.volume = volume
        self.effects = [] if effects is None else effects

    def generate_raw(self, t: np.ndarray) -> np.ndarray:
        return MAX_AMPLITUDE * self.oscillator(t, self.frequency)


class Silence(Playable):
    def __init__(self, start: float = 0.0, length: float = 1.0, volume: float = 1.0, effects: Sequence[Effect] = None):
        self.start = start
        self.length = length
        self.volume = volume
        self.effects = [] if effects is None else effects

    def generate_raw(self, t: np.ndarray) -> np.ndarray:
        return np.zeros(t.shape)
