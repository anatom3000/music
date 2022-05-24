import numpy as np

import oscillators
import synth
from playing import SAMPLE_RATE, play_from_array

NB_HARMONIQUE = 4

bpm = 60
song = "c3 e3 f3 g3 a3 b3".split() * 1
env = synth.Enveloppe(attack=0.1, decay=0.1, sustain=0.7, release=0.1)

sound = np.array([])

for note in song:
    base = synth.Note.from_string(note, env, bpm, oscillators.sine)
    t = np.linspace(0, base.total_length, int(base.total_length*SAMPLE_RATE))

    note_sound = base.generate(t)
    print("Generating...")

    sound = np.append(sound, note_sound)

play_from_array(sound)
