from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from typing import Union, Optional, Callable

from synth.playables import Playable
from synth.constants import EPSILON


class Tone:
    TONES_ID = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}

    def __init__(self, tid):
        self.id = tid

    @classmethod
    def from_notation(cls, tone: str, octave: int, *, flat: bool = False, sharp: bool = False):
        return cls(cls.id_from_notation(tone, octave, flat=flat, sharp=sharp))

    @classmethod
    def from_string(cls, note: str) -> "Tone":
        if note[1] in '#b':
            return cls.from_notation(note[0], int(note[2]), flat=note[1] == 'b', sharp=note[1] == '#')
        return cls.from_notation(note[0], int(note[1]))

    @property
    def frequency(self) -> float:
        return self.id_to_freqency(self.id)

    @staticmethod
    def id_to_freqency(tid):
        return 440 * 2 ** ((tid - 69) / 12)

    @staticmethod
    def to_rel_frequency(st: Union[float, np.ndarray]):
        return 2 ** (st / 12)

    @staticmethod
    def id_from_notation(tone: str, octave: int, *, flat: bool = False, sharp: bool = False) -> int:
        return 12 * (octave + 1) + Tone.TONES_ID[tone.lower()] + sharp - flat


class ADSR:
    """
    Modified version of the ADSR class from torchsynth
        => https://github.com/torchsynth/torchsynth/blob/4f3be6532a80b3298958eb5eca2f653a80ec7562/torchsynth/module.py#L317=
    Can be used for the pitch or the amplitude enveloppe
    """

    def __init__(self, *, attack: float, decay: float, sustain: float, release: float, level: float = 1.0):
        self.attack = attack + EPSILON
        self.decay = decay + EPSILON
        self.sustain = sustain + EPSILON
        self.release = release + EPSILON
        self.level = level

    def get(self, t: np.ndarray, duration: Union[np.ndarray, float]) -> np.ndarray:
        # Calculations to accommodate attack/decay phase cut by note duration.
        new_attack = np.minimum(self.attack, duration)
        new_decay = np.clip(duration - self.attack, 0.0, self.decay)

        attack_signal = ADSR.ramp(t, new_attack)

        a = 1.0 - self.sustain
        b = self.ramp(t, new_decay, start=new_attack, inverse=True)
        decay_signal = a * b + self.sustain

        release_signal = self.ramp(t, self.release, start=duration, inverse=True)

        return attack_signal * decay_signal * release_signal * self.level

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


@dataclass
class Harmonic:
    frequency: float
    amplitude: float
    oscillator: Callable[[np.ndarray, float], np.ndarray]


@dataclass
class Timbre:
    pitch_enveloppe: ADSR
    amplitude_enveloppe: ADSR
    harmonics: Iterable[Harmonic]


class Note(Playable):
    def __init__(self, tone: Tone, timbre: Timbre, start: float = 0.0, length: float = 1.0):
        self.tone = tone
        self.timbre = timbre

        self.start = start
        self.raw_length = length
        self.length = self.raw_length + self.timbre.amplitude_enveloppe.release

    def generate(self, t: np.ndarray, max_amplitude: int) -> np.ndarray:
        # terrible, unoptimized code
        # if a numpy nerd can fix this I'd be grateful
        # (at least it works?)
        sound = np.zeros(t.shape)
        for h in self.timbre.harmonics:
            sound += h.amplitude * h.oscillator(t, h.frequency * self.tone.frequency * Tone.to_rel_frequency(self.timbre.pitch_enveloppe.get(t, self.raw_length)))

        sound *= self.timbre.amplitude_enveloppe.get(t, self.raw_length)
        sound *= max_amplitude / np.max(sound)

        return sound.astype(np.int16)
