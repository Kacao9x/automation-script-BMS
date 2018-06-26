#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
TITAN Web Interface
See Github repo for documentation
'''

import unittest

import numpy as np
from numpy import convolve as np_convolve
from scipy.signal import fftconvolve, lfilter, firwin, upfirdn
from scipy.signal import convolve as sig_convolve
from scipy.ndimage import convolve1d

class echoes_signals(object):
    '''
    echoes_signals contains signal processing algorithms for the EchOES platform
    '''

    _Fs = 2400000.0
    _data = []

    def __init__(self, sample_rate ):
        '''
        Constructor
        '''

        self._Fs = float(sample_rate)
        self._NyqRate = self._Fs * 0.5;
  
    # Comment
    def close(self):
        return True


    def createEnvelope( self, x, decay ):
        
        out = [0]*(pagesToRead*SPI_BLOCKSIZE_BYTES/2)
        for s in x:
            pass


    def createFirFilter( self, cutoffHz, taps, type ):

        if type == "lowpass":
            cutoffHz = float(cutoffHz)
            b = firwin(taps, cutoffHz / self._Fs )     
        elif type == "highpass":
            cutoffHz = float(cutoffHz)
            b = firwin(taps, cutoffHz / self._Fs, pass_zero=False)     
        elif type == "bandpass":
            cutoffHz = [float(a) / self._Fs for a in cutoffHz]
            b = firwin(taps, cutoffHz, pass_zero=False)     

        return b      

    def applyFirFilter(self, x, b):
        filtered_x = lfilter(b, 1.0, x)
        return filtered_x

    def upsample(self, x, upsampling_rate):
        b = firwin(101, 1.0 / upsampling_rate ) 
        y = upfirdn(b, x, up=upsampling_rate)
        return y
 
    def applyBandpass(self, x):
        filterlen = 65
        b = self.createFirFilter( [ 600000.0, 1100000.0], filterlen, "bandpass")
        y = lfilter(b, 1.0, x)
        return y[filterlen-1:len(y)-1]

    # Removes the DC offset from a signal
    def removeDcOffset(self, x):
        if True:
            avg = sum(x)/float(len(x))
            x[:] = [i - avg for i in x]
            return x
        else:
            filterlen = 501
            b = self.createFirFilter( 50000.0, 31, "highpass")
            y = lfilter(b, 1.0, x)

            return y[filterlen-1:len(y)-1]

    def normalize(self, x):
        xabs = map(abs, x)
        maxval = max(xabs)
        if maxval > 0:
            x = x / maxval
        return x 

class Test(unittest.TestCase):

    def testIt(self):

        print "Running test sequence"


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()        