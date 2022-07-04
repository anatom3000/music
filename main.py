from synth import Song
from synth.oscillators import *
from synth.note import *
from synth.playables import Sample


def main() -> None:
    bpm = 50
    melody = "c4 e4 g4 "*4
    timbre = Timbre(
        amplitude_enveloppe=ADSR(attack=.05, decay=.05, sustain=0.7, release=.1),
        pitch_enveloppe=ADSR(attack=0.0, decay=0.2, sustain=0.0, release=.1, level=1),
        harmonics=np.array(
            [[1, 1.0, sawtooth], [2, 1.0, sine]]
        )
    )

    song = Song.from_lines(bpm, [
        (timbre, melody)
    ])
    song.add([Sample("samples/unity_mono_44.1k.wav", length=60/bpm, start=i*60/bpm) for i in range(5)])
    song.generate_and_play(debug=True)


if __name__ == '__main__':
    main()
