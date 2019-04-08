from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

from scipy import fftpack



def plot_signal():

    # Open file and retrieve the data
    filepath = '/media/kacao/1AFE3614FE35E921/Users/Farmer/Desktop/cycle1-primary.dat'
    with open(filepath) as my_file:
        y_str = my_file.read()
        y_str = y_str.splitlines()
    my_file.close()

    data = np.array([float(num) for num in y_str])                                        # Convert string to float
    
    ped = 1e6/7200000                                                           # Convert micro-sec to sec
    x_1 = np.arange(0, ped * len(data), ped)
    plt.plot(x_1, data)
    plt.title(' Echo-A | Raw [0.3 - 2.6] Mhz | Gain 0.65')
    
    plt.xlim(0, 50)
    plt.xlabel('time (usec)')
    plt.ylabel('amplitude')
    plt.grid('on')
    plt.legend(loc='upper right')
    plt.show()


def discrete_fft():
    filepath = '/media/kacao/1AFE3614FE35E921/Users/Farmer/Desktop/cycle1-primary.dat'
    with open(filepath) as my_file:
        y_str = my_file.read()
        y_str = y_str.splitlines()
    my_file.close()

    data = np.array([float(num) for num in y_str])                                        # Convert string to float
    
    f_s = 7.2
    ped = 1/f_s
    t = np.linspace(0, 2, 2*f_s, endpoint=False)

    X = fftpack.fft(data)
    freqs = fftpack.fftfreq(len(data)) * f_s

    fig, ax = plt.subplots()
    ax.stem(freqs, np.abs(X))
    ax.set_xlabel('Frequency in Hertz [Hz]')
    ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
    ax.set_xlim(-f_s / 2, f_s / 2)

    plt.show()

    return


if __name__ == "__main__":
    discrete_fft()