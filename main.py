import numpy as np

import oscillators
from string_synth_utils import song_from_lines
from synth import Timbre, ADSR

bpm = 240
melody = "c4 c4 c4 d4 2*e4 2*d4 c4 e4 d4 d4 4*c4"
timbre = Timbre(
    enveloppe=ADSR(attack=.08, decay=.2, sustain=1.0, release=.05),
    harmonics=np.array(
        [[1, 1.0, oscillators.sine], [1, 1.4, oscillators.triangle],
         [2, 0.1, oscillators.triangle], [2, 0.14, oscillators.sine]]
    )
)

song = song_from_lines(bpm, [
    (timbre, melody)
])
song.generate_and_play()

print("Finished playing!")
