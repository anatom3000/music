
# the sound library
# import wave, struct

# the cooler sound library
import numpy as np, simpleaudio as sa

from math import cos, pi

TONES = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}

def get_note(tone, octave, bemol=False, sharp=False):

    return 12*(octave+1) + TONES[tone.lower()] + sharp - bemol


def get_freq(note):
    return 440 * 2 ** ((note-69)/12)

def tune(freqs, a, t):
    return int(sum([
        (a/len(freqs))*cos(t*2*pi*f)
        for f in freqs
    ]))

def note():
    return int(sum([
        0
        for af in freqs.items()
    ]))


sample_rate = 44100 # Hz
amplitude = 32767

duration = 2

t = np.arange(0, duration, 1/sample_rate)
print(t)

for note in TONES:
    for i in range(duration*sample_rate):
        t = i/sample_rate
        chords = [ get_freq(get_note(note, i+2, bemol=True)) for i in range(int(t+1))]
        value = tune(chords, amplitude, t)

"""
# calculate note frequencies
A_freq = 440
Csh_freq = A_freq * 2 ** (4 / 12)
E_freq = A_freq * 2 ** (7 / 12)

# get timesteps for each sample, T is note duration in seconds
sample_rate = 44100
T = 0.25
t = np.arange(0, T, sample_rate)

# generate sine wave notes
A_note = np.sin(A_freq * t * 2 * np.pi)
Csh_note = np.sin(Csh_freq * t * 2 * np.pi)
E_note = np.sin(E_freq * t * 2 * np.pi)

# concatenate notes
audio = np.hstack((A_note, Csh_note, E_note))
# normalize to 16-bit range
audio *= 32767 / np.max(np.abs(audio))
# convert to 16-bit data
audio = audio.astype(np.int16)

# start playback
play_obj = sa.play_buffer(audio, 1, 2, sample_rate)

# wait for playback to finish before exiting
play_obj.wait_done()"""