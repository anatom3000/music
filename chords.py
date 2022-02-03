import wave, struct

from math import cos, pi
from sys import argv



middle_c = 261.63/2

chords = [
    (1, 1),
    #(16, 15),
    (9, 8),
    # (6, 5),
    (5, 4),
    (4, 3),
    # (42, 32),
    (3, 2),
    #(8, 5),
    (5, 3),
    #(9, 5),
    (15, 8),
    (2, 1)
]

def tune(freqs, a, t):
    return int(sum([
        (a/len(freqs))*cos(t*2*pi*f)
        for f in freqs
    ]))


sampleRate = 44100 # Hz
amplitude = 32767

duration = 1


obj = wave.open(argv[0].split("/")[-1].split(".")[0]+".wav",'w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(sampleRate)


for c in chords:
    for i in range(duration*sampleRate):
        t = i/sampleRate

        chords = [ middle_c*c[0]/c[1] ]

        value = tune(chords, amplitude, t)

        obj.writeframesraw( struct.pack('<h', int(value)) )

obj.close()