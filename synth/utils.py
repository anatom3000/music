from typing import Iterable

from synth import Song
from synth.note import Timbre, Tone, Note


def song_from_lines(bpm: int, lines: Iterable[tuple[Timbre, str]]) -> Song:
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
                tone=tone_from_string(tone_string),
                timbre=timbre,
                start=t * 60 / bpm,
                length=note_length * 60 / bpm,
            ))
            t += note_length

    return Song(notes)


def tone_from_string(note: str) -> Tone:
    if note[1] in '#b':
        return Tone(note[0], int(note[2]), flat=note[1] == 'b', sharp=note[1] == '#')
    return Tone(note[0], int(note[1]))
