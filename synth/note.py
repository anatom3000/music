from dataclasses import dataclass

import numpy as np
from typing import Union, Optional

from synth import Playable
from synth.constants import EPSILON


class Tone:
    TONES_ID = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}

    def __init__(self, tone: str, octave: int, *, flat: bool = False, sharp: bool = False):
        self.tone = tone
        self.octave = octave
        self.flat = flat
        self.sharp = sharp

        self.id = Tone._get_note_id(tone, octave, flat=flat, sharp=sharp)
        self.frequency = Tone._get_frequency_from_id(self.id)

    @staticmethod
    def _get_frequency_from_id(id: int, /) -> float:
        return 440 * 2 ** ((id - 69) / 12)

    @staticmethod
    def _get_note_id(tone: str, octave: int, *, flat: bool = False, sharp: bool = False) -> int:
        return 12 * (octave + 1) + Tone.TONES_ID[tone.lower()] + sharp - flat

class ADSR:
    """
    Modified version of the ADSR class from torchsynth
        => https://github.com/torchsynth/torchsynth/blob/4f3be6532a80b3298958eb5eca2f653a80ec7562/torchsynth/module.py#L317=
    Can be used for the pitch or the amplitude enveloppe
    """

    def __init__(self, *, attack: float, decay: float, sustain: float, release: float):
        self.attack = attack + EPSILON
        self.decay = decay + EPSILON
        self.sustain = sustain + EPSILON
        self.release = release + EPSILON

    def get(self, t: np.ndarray, duration: Union[np.ndarray, float]) -> np.ndarray:
        # Calculations to accommodate attack/decay phase cut by note duration.
        new_attack = np.minimum(self.attack, duration)
        new_decay = np.clip(duration - self.attack, 0.0, self.decay)

        attack_signal = ADSR.ramp(t, new_attack)

        a = 1.0 - self.sustain
        b = self.ramp(t, new_decay, start=new_attack, inverse=True)
        decay_signal = a * b + self.sustain

        release_signal = self.ramp(t, self.release, start=duration, inverse=True)

        return attack_signal * decay_signal * release_signal

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
class Timbre:
    enveloppe: ADSR
    harmonics: np.ndarray


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
