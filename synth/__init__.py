from collections.abc import Sequence
from typing import Union, Iterable

import numpy as np
import pygame

from synth.note import Timbre, Tone, Note
from synth.playables import Playable
from synth.constants import SAMPLE_RATE, MAX_AMPLITUDE

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, allowedchanges=0)
pygame.init()


class Song:
    def __init__(self, notes: Sequence[Playable]):
        self.notes = sorted(notes, key=lambda x: x.start)
        self.length = max(map(lambda x: x.start + x.length, self.notes))

        self.min_buffer_time = 1.0
        self.extra_time = 1.0

        self.time_generated = 0.0

    def add(self, playable: Union[Playable, Sequence[Playable]]):
        if isinstance(playable, Sequence):
            self.notes.extend(playable)
        else:
            self.notes.append(playable)

        self.length = max(map(lambda x: x.start + x.length, self.notes))

    def generate(self) -> np.ndarray:
        t = np.linspace(0, self.length, round((self.length * SAMPLE_RATE)))
        samples = np.zeros(t.shape, dtype=np.int16)
        for i in self.notes:
            sampled_start = round(SAMPLE_RATE * note.start)

            samples[sampled_start:] += note.generate(t[sampled_start:] - note.start, MAX_AMPLITUDE)
            samples.clip(-MAX_AMPLITUDE, MAX_AMPLITUDE)

            self.time_generated = note.start

        return samples

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
        Song.play(samples, wait=wait)
        if debug:
            print("Finished playing!")

    @classmethod
    def from_lines(cls, bpm: int, lines: Iterable[tuple[Timbre, str]]) -> "Song":
        notes = []
        for line in lines:
            timbre = line[0]
            line_notes = line[1].split()
            t = 0.0
            for n in line_notes:
                if n.count('-') == len(n):
                    t += n.count('-')
                    continue

                note_split = n.split('*')
                if len(note_split) == 1:
                    tone_string = note_split[0]
                    note_length = 1.0
                else:
                    tone_string = note_split[1]
                    note_length = float(note_split[0])

                notes.append(Note(
                    tone=Tone.from_string(tone_string),
                    timbre=timbre,
                    start=t * 60 / bpm,
                    length=note_length * 60 / bpm,
                ))
                t += note_length

        return cls(notes)
