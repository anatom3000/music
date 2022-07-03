from dataclasses import dataclass

import numpy as np

from synth.modulators import ADSR


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


@dataclass
class Timbre:
    enveloppe: ADSR
    harmonics: np.ndarray
