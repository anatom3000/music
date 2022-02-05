import numpy as np
import simpleaudio as sa

from typing import Callable, Union

TONES = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}


def Note(tone: str, octave: int, bemol: bool = False, sharp: bool = False) -> int:
    return 12 * (octave + 1) + TONES[tone.lower()] + sharp - bemol


def get_frequency_from_note(note: int) -> float:
    return 440 * 2 ** ((note - 69) / 12)


def generate_note(t: float, note: int, amplitude: float = 1.0, freqency_mode: bool = False, timbre: Callable[[float], float] = np.sin) -> float:
    if not freqency_mode:
        note = get_frequency_from_note(note)

    return amplitude * timbre(t * 2 * np.pi * note)


def mix_notes(t: float, notes: Union[list[int], dict[int, float]]) -> np.array:
    generated_notes = []
    if isinstance(notes, dict):
        for note, amplitude in notes:
            generated_notes.append(generate_note(t, note, amplitude=amplitude))
    else:
        for note in notes:
            generated_notes.append(generate_note(t, note))

    audio = generated_notes[0]
    for n in generated_notes[1:]:
        audio = audio + n
    # normalize to 16-bit range
    audio *= 32767 / np.max(np.abs(audio))
    # convert to 16-bit data
    audio = audio.astype(np.int16)
    return audio

def play_sound(sound: np.array, sample_rate: int = 44100, wait: bool = True) -> None:
    # start playback
    play_obj = sa.play_buffer(sound, 1, 2, sample_rate)
    # wait for playback to finish before exiting
    if wait:
        play_obj.wait_done()


sample_rate = 44100  # Hz
max_amplitude = 32767

duration = 2

if __name__ == "__main__":
    t = np.arange(duration * sample_rate) / sample_rate
    sound = mix_notes(t, [
        Note("c", 4),
        Note("e", 4),
        Note('a', 4),
    ])
    print(sound)
    play_sound(sound)