import numpy as np

import oscillators
import synth
from playing import SAMPLE_RATE, play_from_array
from synth import Tone

NB_HARMONIQUE = 4

bpm = 240
song = "c3 e3 f3 g3 a3 b3".split() * 10
env = synth.Enveloppe(attack=0.05, decay=0.1, sustain=0.2, release=0.1)
env = synth.Enveloppe(attack=0.0, decay=0.0, sustain=1.0, release=0.0)

sound = np.array([])

for i, note in enumerate(song):
    base = synth.Note.from_string(note, env, 60 / bpm - env.release, oscillators.sawtooth)
    t = np.arange(0, base.total_lenght, 1 / SAMPLE_RATE)

    sound = np.append(sound, base(t))

play_from_array(sound)
