import numpy as np

from synth.oscillators import *
from synth.utils import *
from synth.note import *


def main() -> None:
    bpm = 240
    melody = " ".join(f"c{i}" for i in 8 * list(range(1, 7)))
    timbre = Timbre(
        enveloppe=ADSR(attack=.05, decay=.05, sustain=0.7, release=.1),
        harmonics=np.array(
            [[1, 1.0, sawtooth], [2, 1.0, sine]]
        )
    )

    song = song_from_lines(bpm, [
        (timbre, melody)
    ])
    song.generate_and_play(debug=True)


if __name__ == '__main__':
    main()
