import math

__all__ = ['Tone', 'Enveloppe', 'Note']

import numpy as np

import oscillators

TONES_ID = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}


class Tone:
    def __init__(self, tone, octave, bemol=False, sharp=False):
        self.tone = tone
        self.octave = octave
        self.bemol = bemol
        self.sharp = sharp

        self.id = Tone._get_note_id(tone, octave, bemol, sharp)
        self.frequency = Tone._get_frequency_from_id(self.id)

    @classmethod
    def from_string(cls, note):
        if note[1] in '#b':
            return cls(note[0], int(note[2]), bemol=note[1] == 'b', sharp=note[1] == '#')
        return cls(note[0], int(note[1]))

    @staticmethod
    def _get_frequency_from_id(note_id):
        return 440 * 2 ** ((note_id - 69) / 12)

    @staticmethod
    def _get_note_id(tone, octave, bemol=False, sharp=False):
        return 12 * (octave + 1) + TONES_ID[tone.lower()] + sharp - bemol


class Enveloppe:
    def __init__(self, attack, decay, sustain, release):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def __call__(self, t, lenght=math.inf):
        # release
        if t > lenght:
            return self.sustain * (1 - (t - lenght) / self.release)
        # attack
        if t < self.attack:
            return t / self.attack
        t -= self.attack
        # decay
        if t < self.decay:
            return (self.sustain - 1.0) * t / self.decay + 1.0
        # hold
        return self.sustain

class Note:
    def __init__(self, tone, enveloppe, lenght, oscillator=oscillators.sine):
        self.tone = tone
        self.enveloppe = enveloppe
        self.oscillator = oscillator
        self.lenght = lenght

        self.total_lenght = self.lenght + self.enveloppe.release

    @classmethod
    def from_string(cls, tone, *args, **kwargs):
        return cls(Tone.from_string(tone), *args, **kwargs)

    def __call__(self, t):
        return np.vectorize(self.enveloppe)(t, self.lenght) * self.oscillator(t, self.tone.frequency)
