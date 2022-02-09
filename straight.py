import wave, struct

from sys import argv

sampleRate = 44100 # Hz
amplitude = 32767

duration = 10


obj = wave.open(argv[0].split("/")[-1].split(".")[0]+".wav",'w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(sampleRate)


for i in range(duration*sampleRate):
    t = i/sampleRate

    value = amplitude

    obj.writeframesraw( struct.pack('<h', int(value)) )

obj.close()