from collections import namedtuple

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

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


def normalize(arr, volume=1.0):
    arr = arr / np.max(arr)
    arr *= MAX_AMPLITUDE * volume
    return arr


class Tone:
    def __init__(self, tone, octave, flat=False, sharp=False):
        self.tone = tone
        self.octave = octave
        self.flat = flat
        self.sharp = sharp

        self.id = Tone._get_note_id(tone, octave, flat, sharp)
        self.frequency = Tone._get_frequency_from_id(self.id)

    @staticmethod
    def _get_frequency_from_id(note_id):
        return 440 * 2 ** ((note_id - 69) / 12)

    @staticmethod
    def _get_note_id(tone, octave, flat=False, sharp=False):
        return 12 * (octave + 1) + TONES_ID[tone.lower()] + sharp - flat


def ramp(t, duration=None, start=0, inverse=False):
    duration = t.shape[0] if duration is None else duration

    y = t - start
    y = np.clip(y / duration, 0.0, 1.0)

    if inverse:
        y = np.where(duration > 0.0, 1.0 - y, y)

    return y


class ADSR:
    """
    Modified version of the ADSR class from torchsynth
        => https://github.com/torchsynth/torchsynth/blob/4f3be6532a80b3298958eb5eca2f653a80ec7562/torchsynth/module.py#L317=
    """

    def __init__(self, attack=0.05, decay=0.0, sustain=1.0, release=0.05):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def get(self, t, duration: np.array) -> np.array:
        # Calculations to accommodate attack/decay phase cut by note duration.
        new_attack = np.minimum(self.attack, duration)
        new_decay = np.clip(duration - self.attack, 0.0, self.decay)

        attack_signal = ramp(t, new_attack)

        a = 1.0 - self.sustain
        b = ramp(t, new_decay, start=new_attack, inverse=True)
        decay_signal = a * b + self.sustain

        release_signal = ramp(t, self.release, start=duration, inverse=True)

        return attack_signal * decay_signal * release_signal


# don't question this
Timbre = namedtuple('Timbre', ['enveloppe', 'harmonics'])


class Note:
    def __init__(self, tone: Tone, timbre: Timbre, start: float = 0.0, length: float = 1.0):
        self.tone = tone
        self.timbre = timbre

        self.start = start
        self.raw_length = length
        self.length = self.raw_length + self.timbre.enveloppe.release

    def generate(self, t):
        # terrible, unoptimized code
        # if a numpy nerd can fix this I'd be grateful
        # (at least it works ?)
        # update: it's way too slow :/
        sound = np.zeros(t.shape)
        for relative_frequency, relative_amplitude, oscillator in self.timbre.harmonics:
            sound += relative_amplitude * oscillator(t, relative_frequency * self.tone.frequency)
        return self.timbre.enveloppe.get(t, self.raw_length) * sound

    def get_length(self):
        return self.length + self.timbre.enveloppe.release


class Song:
    def __init__(self, notes):
        self.notes = sorted(notes, key=lambda x: x.start)
        self.length = max(map(lambda x: x.start + x.get_length(), self.notes))

        self.min_buffer_time = 1.0
        self.extra_time = 1.0

        self.sound = pygame.sndarray.make_sound(np.zeros(round(self.length * SAMPLE_RATE), dtype=np.int16))
        self.samples = pygame.sndarray.samples(self.sound)
        self.time_generated = 0.0

    def generate_and_play(self, wait=True):
        started_playing = False
        t = np.linspace(0, self.length, round((self.length * SAMPLE_RATE)))
        for i, note in enumerate(self.notes):
            if (not started_playing) and self.time_generated >= self.min_buffer_time:
                self.sound.play(-1)
                started_playing = True

            sampled_start = round(SAMPLE_RATE * note.start)

            sampled_audio = note.generate(t[sampled_start:] - note.start)
            sampled_audio *= MAX_AMPLITUDE / np.max(sampled_audio)

            self.samples[sampled_start:] += sampled_audio.astype(np.int16)
            self.samples.clip(-MAX_AMPLITUDE, MAX_AMPLITUDE)

            self.time_generated = note.start

        if not started_playing:
            self.sound.play(-1)
        if wait:
            pygame.time.wait(int(self.length * 1000))
            pygame.mixer.stop()

