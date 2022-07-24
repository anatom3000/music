

def main() -> None:
    from synth import Song, Timbre, ADSR, Harmonic
    import synth.oscillators as osc
    import synth.effects as eff

    bpm = 360
    melody = "C4 E4 Ab4 B4"*4
    timbre = Timbre(
        amplitude_enveloppe=ADSR(attack=.05, decay=.05, sustain=0.7, release=.1),
        pitch_enveloppe=ADSR(attack=0.0, decay=0.0, sustain=0.0, release=.0, level=1),
        harmonics=[
            Harmonic(frequency=1, amplitude=1.0, oscillator=osc.sawtooth),
            Harmonic(frequency=2, amplitude=1.0, oscillator=osc.sine)
        ],
        effects=[
            eff.Noise(1e-4)
        ]
    )

    Song.from_lines(bpm, [(timbre, melody)]).generate_and_play(debug=True)


if __name__ == '__main__':
    main()
