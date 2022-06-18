import numpy as np

import oscillators
from string_synth_utils import song_from_lines
from synth import Timbre, ADSR

bpm = 360
melody = "c4 c4 c4 d4 2*e4 2*d4 c4 e4 d4 d4 4*c4"
timbre = Timbre(
    enveloppe=ADSR(attack=0.1, decay=.1, sustain=0.8, release=0.1),
    harmonics=np.array(
        [[1, 0.5, oscillators.sine], [2, 1, oscillators.sine], [3, 0.5, oscillators.sine], [4, 0.25, oscillators.sine],
         [0.5, 0, oscillators.sine]])
)

song = song_from_lines(bpm, (timbre, melody))
song.generate_and_play()

print("Finished playing!")
