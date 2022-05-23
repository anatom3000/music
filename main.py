#!/usr/bin/env python3
"""Play a sine signal."""

# backend/audio imports
import numpy as np
import sounddevice as sd
import time
import sys

from dataclasses import dataclass


samplerate = 44100
start_idx = 0
max_amplitude = 32767
frequency_of_a = 440


@dataclass
class Envelope:
    max_amplitude: float
    attack_time: float
    decay_time: float
    sustain_amplitude: float
    release_time: float

    def get_amplitude(self, t, hold=0):
        return np.array(list(map(lambda x: self.get_single_amplitude(x, hold), t)))

    def get_single_amplitude(self, t, hold=0):
        #return np.array([self.sustain_amplitude])
        if hold:
            if t < self.attack_time:
                return t * self.max_amplitude
            elif t < self.decay_time:
                return (self.sustain_amplitude - self.max_amplitude) * (t - self.attack_time)
            else:
                return np.array([self.sustain_amplitude]) # i dont even know why im supposed to return an array (help)
        else:
            return -self.max_amplitude * (t - hold)


class Note:
    def __init__(self, envelope, frequency, volume=1.0, sample_rate=44100):
        self.envelope = envelope
        self.frequency = frequency
        self.volume = volume
        self.sample_rate = sample_rate

        # internal attributes to play the note


    def generate_sound(self, outdata, frames, _time, status):
        if status:
            print(status, file=sys.stderr)
        t = (self._total_frames + np.arange(frames)) / self.sample_rate
        t = t.reshape(-1, 1)

        outdata[:] = np.multiply(np.sin(2 * np.pi * self.frequency * t), self.envelope.get_amplitude(t, self._holding))
        self._total_frames += frames

    def play(self):
        self._holding = True
        self._total_frames = 0
        self._stream = sd.OutputStream(channels=1, callback=self.generate_sound, samplerate=self.sample_rate)

        self._stream.start()
    
    def release(self):
        self._holding = False
        time.sleep(self.envelope.release_time)
        self._stream.stop()

## FRONT END²
def pygame_frontend():
    # frontend imports
    import pygame

    pygame.init()

    our_env = Envelope(max_amplitude/2, 0.1, 0.1, max_amplitude/3, 0.2)
    our_note = Note(our_env, frequency_of_a)

    screen = pygame.display.set_mode((640, 480))
    COLOR = (0,0,0)
    running = True
    holding = False
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if not holding:
                    holding = True
                    our_note.play()
                    print("playing!")
                COLOR = (255, 255, 255)
            if e.type == pygame.MOUSEBUTTONUP:
                our_note.release()
                COLOR = (0,0,0)
                holding = False
                print("releasing!")
        screen.fill(COLOR)


    pygame.quit()

our_env = Envelope(max_amplitude/2, 1, 1, max_amplitude/3, 1)
our_note = Note(our_env, frequency_of_a)
our_note.play()
time.sleep(5) # hold for 2 secs
our_note.release()