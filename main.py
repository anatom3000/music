

def main() -> None:
    # from synth import Song, Timbre
    # from synth.note import ADSR, Harmonic
    # from synth.oscillators import sawtooth, sine
    from synth.playables import Sample

    # bpm = 50
    # melody = "C4 E4 Ab4 B4"*4
    # timbre = Timbre(
    #     amplitude_enveloppe=ADSR(attack=.05, decay=.05, sustain=0.7, release=.1),
    #     pitch_enveloppe=ADSR(attack=0.0, decay=0.0, sustain=0.0, release=.0, level=1),
    #     harmonics=[
    #         Harmonic(frequency=1, amplitude=1.0, oscillator=sawtooth),
    #         Harmonic(frequency=2, amplitude=1.0, oscillator=sine)
    #     ]
    # )

    # song = Song.from_lines(bpm, [
    #     (timbre, melody)
    # ])
    # song.add([Sample("samples/unity_mono_44.1k.wav", length=60/bpm, start=i*60/bpm) for i in range(5)])
    # song.generate_and_play(debug=True)

    Sample("samples/unity_mono_44.1k.wav").generate_and_play()

if __name__ == '__main__':
    main()
