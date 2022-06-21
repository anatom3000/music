from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import pygame

SAMPLE_RATE = 44100  # Hz
MAX_AMPLITUDE = 4096
TONES_ID = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}
EPSILON = 1e-6

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


def normalize(arr: np.ndarray, *, volume: float = 1.0) -> np.ndarray:
    arr = arr / np.max(arr)
    arr *= MAX_AMPLITUDE * volume
    return arr


def ramp(t: np.ndarray, duration: Optional[Union[np.ndarray, float]] = None, start: Union[np.ndarray, float] = 0.0,
         inverse: bool = False) -> np.ndarray:
    duration = t.shape[0] if duration is None else duration

    y = t - start
    y = np.clip(y / duration, 0.0, 1.0)

    if inverse:
        y = np.where(duration > 0.0, 1.0 - y, y)

    return y


def play(samples: np.ndarray, *, wait: bool = True) -> None:
    sound = pygame.sndarray.make_sound(samples)
    sound.play(-1)
    if wait:
        pygame.time.wait(int(samples.shape[0] / SAMPLE_RATE * 1000))
        pygame.mixer.stop()


class Tone:
    def __init__(self, tone: str, octave: int, *, flat: bool = False, sharp: bool = False):
        self.tone = tone
        self.octave = octave
        self.flat = flat
        self.sharp = sharp

        self.id = Tone._get_note_id(tone, octave, flat=flat, sharp=sharp)
        self.frequency = Tone._get_frequency_from_id(self.id)

    @staticmethod
    def _get_frequency_from_id(note_id: int, /) -> float:
        return 440 * 2 ** ((note_id - 69) / 12)

    @staticmethod
    def _get_note_id(tone: str, octave: int, *, flat: bool = False, sharp: bool = False) -> int:
        return 12 * (octave + 1) + TONES_ID[tone.lower()] + sharp - flat


class ADSR:
    """
    Modified version of the ADSR class from torchsynth
        => https://github.com/torchsynth/torchsynth/blob/4f3be6532a80b3298958eb5eca2f653a80ec7562/torchsynth/module.py#L317=
    """

    def __init__(self, *, attack: float = 0.05, decay: float = 0.0, sustain: float = 1.0, release: float = 0.05):
        self.attack = attack + EPSILON
        self.decay = decay + EPSILON
        self.sustain = sustain + EPSILON
        self.release = release + EPSILON

    def get(self, t: np.ndarray, duration: Union[np.ndarray, float]) -> np.ndarray:
        # Calculations to accommodate attack/decay phase cut by note duration.
        new_attack = np.minimum(self.attack, duration)
        new_decay = np.clip(duration - self.attack, 0.0, self.decay)

        attack_signal = ramp(t, new_attack)

        a = 1.0 - self.sustain
        b = ramp(t, new_decay, start=new_attack, inverse=True)
        decay_signal = a * b + self.sustain

        release_signal = ramp(t, self.release, start=duration, inverse=True)

        return attack_signal * decay_signal * release_signal

    def __mul__(self, other: float) -> 'ADSR':
        return self.__class__(self.attack * other, self.decay * other, self.sustain * other, self.release * other)


@dataclass
class Timbre:
    enveloppe: ADSR
    harmonics: np.ndarray


class Note:
    def __init__(self, tone: Tone, timbre: Timbre, start: float = 0.0, length: float = 1.0):
        self.tone = tone
        self.timbre = timbre

        self.start = start
        self.raw_length = length
        self.length = self.raw_length + self.timbre.enveloppe.release

    def generate(self, t: np.ndarray) -> np.ndarray:
        # terrible, unoptimized code
        # if a numpy nerd can fix this I'd be grateful
        # (at least it works ?)
        # update: it's way too slow :/
        sound = np.zeros(t.shape)
        for relative_frequency, relative_amplitude, oscillator in self.timbre.harmonics:
            sound += relative_amplitude * oscillator(t, relative_frequency * self.tone.frequency)
        return self.timbre.enveloppe.get(t, self.raw_length) * sound

    def get_length(self) -> float:
        return self.length + self.timbre.enveloppe.release


class Song:
    def __init__(self, notes: Sequence[Note]):
        self.notes = sorted(notes, key=lambda x: x.start)
        self.length = max(map(lambda x: x.start + x.get_length(), self.notes))

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
