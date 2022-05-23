import wave, struct

from math import cos, pi
from sys import argv

TONES = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}

def get_note(tone, octave, bemol=False, sharp=False):

    return 12*(octave+1) + TONES[tone.lower()] + sharp - bemol


def get_freq(note):
    return 440 * 2 ** ((note-69)/12)

def tune(freqs, a, t):
    return int(sum([
        (a/len(freqs))*cos(t*2*pi*f)
        for f in freqs
    ]))


sampleRate = 44100 # Hz
amplitude = 32767

duration = 0.5


obj = wave.open(argv[0].split("/")[-1].split(".")[0]+".wav",'w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(sampleRate)

song = "cccdeeddceddcc"

for note in song:
    for i in range(int(duration*sampleRate)):
        t = i/sampleRate

        chords = [ get_freq(get_note(note, 4, bemol=True)) for i in range(int(t+1))]

        value = tune(chords, amplitude, t)

        obj.writeframesraw( struct.pack('<h', int(value)) )

obj.close()