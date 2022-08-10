from __future__ import annotations

from typing import Union

import numpy as np

"""
Module containing various types of oscillators.
"""


def sine(t: np.ndarray, frequency: float | np.ndarray = 1.0) -> np.ndarray:
    return np.sin(t * 2 * np.pi * frequency)


def square(t: np.ndarray, frequency: float | np.ndarray = 1.0) -> np.ndarray:
    return (-1) ** (t * frequency).astype(int)


def triangle(t: np.ndarray, frequency: float | np.ndarray = 1.0) -> np.ndarray:
    return 2 * np.absolute(t * frequency - np.floor(t * frequency + 0.5))


def sawtooth(t: np.ndarray, frequency: float | np.ndarray = 1.0) -> np.ndarray:
    return (frequency * t) % 1


class Pulse:
    """A pulse wave of a give pulse width"""

    def __init__(self, width: float):
        self.width = width

    def __call__(self, t: np.ndarray, frequency: float | np.ndarray = 1.0) -> np.ndarray:
        return 2 * (((t * frequency / 2) % 1) < self.width) - 1
