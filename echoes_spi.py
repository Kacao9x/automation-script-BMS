#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import spidev
import RPi.GPIO as GPIO
import time
from time import sleep
from pprint import pprint

CMD_READ_RESULT = int(0x60)

WAIT_PIN = 27

class spi_echoes(object):
    '''
    spi_echoes is a SPI driver for the EchOES platform used to communicate with
    the STM32 microprocessor
    '''

    _spi = False
    _datarate = False

    def __init__(self, datarate = 1000000):
        '''
        Constructor
        '''

        # Create instance of SPI driver and open it
        self._spi = spidev.SpiDev()
        self._spi.open(0, 0)

        self._datarate = datarate

        # Set our max clock speed
        self._spi.max_speed_hz = self._datarate

        # Set up GPIO wait pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(WAIT_PIN, GPIO.IN)

    def close(self):
        self._spi.close()
        GPIO.cleanup()

    def sendCmd(self, cmd, payload=False):

        # Wait until the wait pin goes low before proceeding
        timeout = 1000000
        while(GPIO.input(WAIT_PIN) and timeout > 0):
            timeout -= 1
        if timeout == 0:
            print("sendCmd - timeout")
            return False

        spi_block = [ 0xAA,0x55, cmd, 0, 0 ]

        if payload:
            spi_block[3] = (payload & 0xFF00) >> 8
            spi_block[4] = (payload & 0xFF)
        
        self._spi.writebytes(spi_block)

        return True

    def receiveData(self, totalbytes):

        # Wait until the wait pin goes low before proceeding
        timeout = 1000000
        while(GPIO.input(WAIT_PIN) and timeout > 0):
            timeout -= 1
        if timeout == 0:
            print("receiveData - timeout")
            return False

        result = self._spi.readbytes(totalbytes)

        #sleep(0.0001)

        return result


class Test(unittest.TestCase):

    def testIt(self):
        # Create new instance with 20MHz clock
        spi = spi_echoes(datarate=16000000)

        if spi.sendCmd(CMD_READ_RESULT):
            output = spi.receiveData(4096)

            pprint(output)
            return True

        return False

        




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


