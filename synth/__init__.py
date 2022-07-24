from collections.abc import Sequence
from typing import Union, Iterable

import numpy as np

from synth.note import Timbre, Tone, Note
from synth.playables import Playable
from synth.constants import SAMPLE_RATE, MAX_AMPLITUDE


class Song(Playable):
    def __init__(self, playables: Sequence[Playable], volume: float = 1.0):
        self.playables = sorted(playables, key=lambda x: x.start)
        self.length = max(map(lambda x: x.start + x.length, self.playables))
        self.volume = volume

        self.min_buffer_time = 1.0
        self.extra_time = 1.0

        self.time_generated = 0.0

    def add(self, playable: Union[Playable, Sequence[Playable]]) -> None:
        if isinstance(playable, Sequence):
            self.playables.extend(playable)
        else:
            self.playables.append(playable)

        self.length = max(map(lambda x: x.start + x.length, self.playables))

    def generate(self) -> np.ndarray:
        t = np.linspace(0, self.length, round((self.length * SAMPLE_RATE)))
        samples = np.zeros(t.shape, dtype=np.int16)
        for p in self.playables:
            sampled_start = round(SAMPLE_RATE * p.start)

            samples[sampled_start:round(sampled_start+p.length*SAMPLE_RATE)] += p.generate()
            samples.clip(-MAX_AMPLITUDE, MAX_AMPLITUDE)

            self.time_generated = p.start

        return samples * self.volume

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
