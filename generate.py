import wave
import numpy as np

from sys import argv


SAMPLE_RATE = 44100 # Hz
MAX_AMPLITUDE = 32767
NB_HARMONIQUE = 4


## NOTE TO FREQUENCY UTILITIES
TONES = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}

def get_note_from_string(note):
    if note[1] in '#b':
        return get_note(note[0], int(note[2]), bemol=note[1]=='sb', sharp=note[1]=='#')
    return get_note(note[0], int(note[1]))

def get_raw_note(tone, octave, bemol=False, sharp=False):
    return 12*(octave+1) + TONES[tone.lower()] + sharp - bemol


def get_freq(note):
    return 440 * 2 ** ((note-69)/12)

def get_note(tone, octave, bemol=False, sharp=False):
    return get_freq(get_raw_note(tone, octave, bemol, sharp))

## WAVE FUNCTIONS
def sine(t, freq):
    return np.sin(t*2*np.pi*freq)

def square(t, freq):
    return 1 if t*freq % 1 < 1/2 else -1

## SOUND GENERATING FUNCTIONS
def tune(t, frequencies, amplitude, wave=sine):
    return amplitude / len(frequencies) * np.sum((wave(t, frequency) for frequency in frequencies))

print("Generating file...")

obj = wave.open("sound.wav",'w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(SAMPLE_RATE)

bpm = 110
song = np.array("c4 c4 c4 d4 e4 e4 d4 d4 c4 e4 d4 d4 c4".split())

for note in song:
    t = np.arange(0, 60/bpm, 1/SAMPLE_RATE)

    base = get_note_from_string(note)
    chords = [ base*(i+1) for i in range(NB_HARMONIQUE) ]

    value = tune(t, chords, MAX_AMPLITUDE)
    for v in value.astype(int):
        obj.writeframesraw( wave.struct.pack('<h', v) )

obj.close()
print("Done ! Saved to sound.wav")