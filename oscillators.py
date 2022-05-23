import numpy as np


def sine(t, freq):
    return np.sin(t * 2 * np.pi * freq)


def square(t, freq):
    return 1 if t * freq % 1 < (1 / 2) else -1

square = np.vectorize(square)