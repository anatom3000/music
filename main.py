import numpy as np

import oscillators
import synth
from playing import SAMPLE_RATE, play_from_array

NB_HARMONIQUE = 4

bpm = 120
song = "c4 c4 c4 d4 e4 e4 d4 d4 c4 e4 d4 d4 c4".split()
env = synth.Enveloppe(attack=0.0, decay=.02, sustain=0.7, release=0.0)
osc = oscillators.sine
harm = np.array(
    [[2, 1, oscillators.sine], [3, 0.5, osc], [4, 0.25, oscillators.sine], [0.5, 1, oscillators.sine], [1, -0.5, osc]])
harm2 = np.array([[1, -0.5, oscillators.square]])

sound = np.array([])

for note in song:
    base = synth.Note.from_string(note, env, bpm, osc, harm)
    t = np.linspace(0, base.total_length, int(base.total_length * SAMPLE_RATE))

    note_sound = base.generate(t)
    sound = np.append(sound, note_sound)

play_from_array(sound)
