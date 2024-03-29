def main() -> None:
    from synth import Song, Timbre, ADSR, Harmonic
    import synth.oscillators as osc
    import synth.effects as eff

    bpm = 360
    melody = "C4 E4 Ab4 B4" * 4
    timbre = Timbre(
        amplitude_enveloppe=ADSR(attack=.05, decay=.05, sustain=0.7, release=.1),
        pitch_enveloppe=ADSR(attack=0.0, decay=0.0, sustain=0.0, release=.0, level=1),
        harmonics=[
            Harmonic(frequency=1, amplitude=1.0, oscillator=osc.sawtooth),
            Harmonic(frequency=2, amplitude=1.0, oscillator=osc.sine)
        ]
    )
    effects = [
        eff.Noise(1e-4),
        eff.Normalize
    ]

    s = Song.from_lines(bpm, [(timbre, melody, effects)])
    s.generate_and_play(debug=True)


def noise() -> None:
    from synth import Noise

    Noise(length=10.0, volume=1.0).generate_and_save("out/sound.wav")


def sample_transpose() -> None:
    print('a')
    from synth import Sample
    from synth.effects import LowPassFilter
    print("b")
    s = Sample(
        "samples/unity_mono_44.1k.wav",
        effects=[
            LowPassFilter(880, resonance=0.5, resonance_width=220, cutout_width=880),
            # Noise(LFO(frequency=2.0, amplitude=1e-1, center=1e-1))
        ]
    )
    print("c")

    s.generate_and_play()


def scratched_silence() -> None:
    from synth import Silence
    from synth.effects import Scratch
    s = Silence(length=10, effects=[Scratch(1e-2)])
    s.generate_and_play(debug=True)


def gen_a440() -> None:
    from synth import PlayableOscillator
    a440 = PlayableOscillator(frequency=440)
    from synth.effects import Transpose
    a440.effects = [
        Transpose(18),
        Transpose(-18)
    ]
    a440.generate_and_play(debug=True)


def lowpassfilter() -> None:
    from synth import PlayableOscillator
    from synth.effects import LowPassFilter
    import synth.oscillators as osc

    signals = []
    for i in range(8):
        signal = PlayableOscillator(frequency=440, oscillator=osc.sine, length=1.0)
        signal.effects = [
            LowPassFilter(i * 110)  # LinearTransition(0.0, 100.0, signal.length, 1000.0)
        ]
        signals.append(signal.generate())

    print("Finished generating!")

    from synth import Playable
    for s in signals:
        Playable.play(s, wait=True)


def double_unity() -> None:
    from synth import Sample
    unity = Sample("samples/unity_mono_44.1k.wav", length=30)
    unity2 = unity.transposed(-12)
    from synth import Song
    s = Song([unity, unity2])
    s.generate_and_play()


if __name__ == '__main__':
    double_unity()
