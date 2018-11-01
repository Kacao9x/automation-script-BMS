import pandas as pd
import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
import thLib as th

def main():
    # with open(address + '') as my_file:
    #     y_str = my_file.read()
    #     y_str = y_str.splitlines()
    # my_file.close()
    #
    # for i, num in enumerate(y_str):
    #     tC_1.append(num.split()[1])
    #     tC_2.append(num.split()[2])

    # import csv file
    with open(address + 'allRawData.csv') as outfile:
        avgTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()
    print (avgTable.head())

    #FFT
    N = 512
    T = 1.38888889e-7 #float( 1/7200000 )
    x = np.linspace(0, N*T, N)

    while cycle_id < cycle + 1:

        y = avgTable[ str(cycle_id) ]
        y_1 = avgTable[ str(cycle_id + 1) ]

        # perform FFT
        yf = fft( y[180 : ] )
        yf_1 = fft( y_1[180 : ])

        err = np.angle( yf[ 1 : N/2 ] / yf_1[ 1 : N/2 ])
        print ('phase error: %s' % str(err))

        # create new x-axis: freq from signal
        xf = np.linspace( 0.0, 1.0/(2.0*T), N//2 )
        # plot results
        plt.plot( xf, yf[0 : N//2], label = 'signal')
        plt.grid()
        plt.xlabel(' Frequency')
        plt.ylabel(r'Spectral Amplitude')
        plt.legend( loc=1 )
        plt.show()

    return


address = '/media/jean/Data/titan-echo-board/echo-C/background_181024/data/primary/'
echoes_index = []
backgrd = []

cycle = 99
cycle_id = 1


if __name__ == '__main__':
    main()
