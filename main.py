import numpy as np

import oscillators
import synth
from playing import SAMPLE_RATE, play_from_array

NB_HARMONIQUE = 4

bpm = 120
song = "c4 c4 c4 d4 e4 e4 d4 d4 c4 e4 d4 d4 c4".split()

osc = oscillators.sine
harm = np.array(
    [[1, 1, osc], [2, 1, oscillators.sine], [3, 0.5, osc], [4, 0.25, oscillators.sine], [0.5, 1, oscillators.sine], [1, -0.5, osc]])
env = synth.Enveloppe(attack=0.0, decay=.02, sustain=0.7, release=0.0)

timbre = synth.Timbre(enveloppe=env, harmonics=harm)



for note in song:
    base = synth.Note(synth.Tone.from_string(note), timbre=timbre, length=60/bpm)
    t = np.linspace(0, base.length+base.timbre.enveloppe.attack, int((base.length+base.timbre.enveloppe.attack) * SAMPLE_RATE))

    note_sound = base.generate(t)

    play_from_array(note_sound)
