import numpy as np

import oscillators
from synth import Song, Note, Tone, Timbre, pygame, ADSR

bpm = 60
melody = "c4 c4 c4 d4 e4 e4 d4 d4 c4 e4 d4 d4 c4".split()
print(len(melody))
timbre = Timbre(
    enveloppe=ADSR(attack=0.01, decay=.02, sustain=0.7, release=0.1),
    harmonics=np.array([[1, 0.5, oscillators.sine], [2, 1, oscillators.sine], [3, 0.5, oscillators.sine], [4, 0.25, oscillators.sine], [0.5, 1, oscillators.sine]])
)
notes = [
    Note(Tone.from_string(n), timbre, start=i*60/bpm, length=1*60/bpm)
    for i, n in enumerate(melody)
]

song = Song(notes)

song.generate()

while pygame.mixer.get_busy():
    pass
print("Finished playing!")