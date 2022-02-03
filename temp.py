import numpy as np

from matplotlib import pyplot as plt
import numpy as np
from math import pi

x = np.arange(0, 10, 0.05)
func = np.sin(pi*x) + np.sin(2*pi*x)
trans = abs(np.fft.fft(func))

for i in range(20, 50):
	print(i/20, trans[i])