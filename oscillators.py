import numpy as np


def sine(t, frequency):
    return np.sin(t * 2 * np.pi * frequency)


def square(t, frequency):
    return (-1) ** (t * frequency).astype(int)


def triangle(t, frequency):
    return 2 * \
           np.absolute(
               t * frequency
               - np.floor(
                   t * frequency
                   + 0.5
               )
           )


def sawtooth(t, frequency):
    return (frequency * t) % 1
