#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
EchOES protocol for communicating with EchOES board
See Github repo for documentation
'''
import unittest

from echoes_spi import *
from enum import Enum
from time import sleep
import datetime

class Echoes_Spi_Cmds(Enum):
    SPI_CMD_SET_VOLTAGE            = 0x40
    SPI_CMD_SET_IMPULSE_TYPE       = 0x41
    SPI_CMD_SET_IMPULSE_DELAY      = 0x42
    SPI_CMD_SET_IMPULSE_CYCLES     = 0x43
    SPI_CMD_SET_ADC_CONFIG         = 0x44
    SPI_CMD_SET_CAPTURE_ADC        = 0x50
    SPI_CMD_SET_CAPTURE_SEQ_CNT    = 0x51
    SPI_CMD_SET_VGA_GAIN           = 0x52
    SPI_CMD_READ_RESULT            = 0x60
    SPI_CMD_RUN_CAPTURE            = 0x80
    SPI_CMD_RUN_CAPTURE_NO_IMPULSE = 0x81

class Impulse_Type(Enum):
    half = 0
    full = 1

class Impulse_Voltage(Enum):
    impulse_85v = 0
    impulse_80v = 1
    impulse_75v = 2
    impulse_70v = 3
    impulse_65v = 4
    impulse_60v = 5
    impulse_55v = 6
    impulse_50v = 7
    impulse_45v = 8
    impulse_40v = 9
    impulse_35v = 10
    impulse_30v = 11
    impulse_25v = 12
    impulse_20v = 13
    impulse_15v = 14
    impulse_10v = 15

class Capture_Adc(Enum):
    adc_primary = 0
    adc_secondary = 1

class Sequence_Count(Enum):
    sequence_1 = 1
    sequence_2 = 2
    sequence_4 = 4
    sequence_8 = 8
    sequence_16 = 16

class ADC_Config(Enum):
    fs_12bit_2_40msps = 0
    fs_10bit_2_76msps = 1
    fs_08bit_3_27msps = 2
    fs_06bit_4_00msps = 3
    fs_12bit_4_8msps  = 4
    fs_10bit_5_54msps = 5
    fs_08bit_6_55msps = 6
    fs_06bit_8_00msps = 7
    fs_12bit_7_2msps  = 8
    fs_10bit_8_31msps = 9
    fs_08bit_9_82msps = 10
    fs_06bit_12_00msps = 11

SPI_BLOCKSIZE_BYTES = 4096

# This is the UART init command if we decide to ever go back
# uart = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)

class echoes(object):
    '''
    echoes is a driver for the EchOES platform
    '''

    _spiProtocol = False
    _time_adcBufXfer = 0
    _time_adcFloatConvt = 0
    _class = "echoes_protocol"

    def __init__(self ):
        '''
        Constructor
        '''

        # Create instance of SPI driver and open it
        self._spiProtocol = spi_echoes()

    def close(self):
        self._spiProtocol.close()
        return True


    # Sets the type of impulse (half wave or full wave)
    def setImpulseType(self, type ):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_IMPULSE_TYPE, type)


    # Sets the voltage rails for Bam-Bam
    def setImpulseVoltage(self, voltage ):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_VOLTAGE, voltage)


    # Sets the delay (in processor cycles) to determine waveform period
    def setImpulseDelay(self, delay):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_IMPULSE_DELAY, delay)


    # Sets the number of impulses periods / cycles
    def setImpulseCycles(self, cycles):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_IMPULSE_CYCLES, cycles)


    # Sets the number of impulses periods / cycles
    def setAdcConfig(self, adc_config):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_ADC_CONFIG, adc_config)


    # Define which ADC to use for capture
    def setCaptureADC(self, adc):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_CAPTURE_ADC, adc)


    # Define the number of conversion sequences to run
    def setConvertsPerSequence(self, seq):
        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_CAPTURE_SEQ_CNT, seq)


    # Sets the gain of the VGA
    def setVgaGain(self, gain):
        if gain < 0 or gain > 1.0:
            return False

        gain = gain * 255;
        gain = int(gain)

        return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_SET_VGA_GAIN, gain )

    def readAdcData(self, pagesToRead = 32):

        print(str(datetime.datetime.now())+" "+self._class+": Reading data from capture")        
        # Send command to read a given page

        rx_data = []

        t1 = time.time()

        for page in range(0,pagesToRead):
            print(str(datetime.datetime.now())+" "+self._class+": Reading page "+str(page))
            res = self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_READ_RESULT, page )
            if not res:
                print "readAdcData(): timeout error"
                return False
            # print(str(datetime.datetime.now())+" "+self._class+": Reading page "+str(page))
            rx_data.extend(self._spiProtocol.receiveData( SPI_BLOCKSIZE_BYTES ))

        self._time_adcBufXfer = time.time() - t1

        t2 = time.time()

        # pprint(rx_data)
        # return True

        output = [0]*(pagesToRead*SPI_BLOCKSIZE_BYTES/2)
        indx2 = 0
        for indx in range(0,len(rx_data)/2):
            output[indx] = (float(rx_data[indx2] + rx_data[indx2+1]*256)*(1.0/65536.0))
            indx2 += 2

        self._time_adcFloatConvt = time.time() - t2;

        print(str(datetime.datetime.now())+" "+self._class+": Read ADC transfer time:"+str(self._time_adcBufXfer))
        print(str(datetime.datetime.now())+" "+self._class+": Float conversion time:"+str(self._time_adcFloatConvt))

        return output

    def initiateCapture(self, send_impulse = True):


        if send_impulse:
            print(str(datetime.datetime.now())+" "+self._class+": Initiating impulse + capture")
            return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_RUN_CAPTURE )
        else:
            print(str(datetime.datetime.now())+" "+self._class+": Initiating capture only")
            return self._spiProtocol.sendCmd( Echoes_Spi_Cmds.SPI_CMD_RUN_CAPTURE_NO_IMPULSE )

        return True 

  
 
class Test(unittest.TestCase):

    def testIt(self):

        print "Running test sequence"

        # Create new instance with 16MHz SPI clock
        echoes_1 = echoes()

        # Set impulse type to bi-polar
        if not echoes_1.setImpulseType(Impulse_Type.full):
            print "Failed to set impulse type"

        # Set voltage rails to 30V
        if not echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_30v):
            print "Failed to set voltage"

        # Impulse waveform has three periods
        if not echoes_1.setImpulseCycles(3):
            print "Failed to set impulse cycles"

        # Capture on primary (impulse side) ADC first
        if not echoes_1.setCaptureADC(Capture_Adc.adc_primary):
            print "Failed to set capture ADC"

        # Set VGA gain to 0.1 (from 0.0 to 1.0)
        if not echoes_1.setVgaGain(0.5):
            print "Failed to set VGA gain"

        # Average together 4 impulse/capture runs
        if not echoes_1.setConvertsPerSequence(Sequence_Count.sequence_1):
            print "Failed to set conversion count per sequence"

        return

        # Bam-Bam and capture!
        echoes_1.initiateCapture()

        output = echoes_1.readAdcData()



        pprint(output)

        print("Data transfer and float conversion time:")
        pprint(echoes_1._time_adcBufXfer)
        pprint(echoes_1._time_adcFloatConvt)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
