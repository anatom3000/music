import numpy as np
import pygame
import pygame.sndarray

__all__ = ['play_from_array', 'SAMPLE_RATE']

SAMPLE_RATE = 44100  # Hz
MAX_AMPLITUDE = 4096

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1)
pygame.init()


def play_from_array(arr, begin=-1):
    sound_obj = pygame.sndarray.make_sound((MAX_AMPLITUDE * arr).astype(np.int16))
    sound_obj.play(begin)
    pygame.time.delay(int(sound_obj.get_length() * 1000))
    sound_obj.stop()
